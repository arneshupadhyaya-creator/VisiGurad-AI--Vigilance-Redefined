import torch
import torch.nn as nn

from torchvision import models


class SiameseNetwork(nn.Module):

    def __init__(self):

        super().__init__()

        
        # ResNet50 Backbone
        

        resnet = models.resnet50(
            weights=models.ResNet50_Weights.DEFAULT
        )

        self.backbone = nn.Sequential(
            *list(resnet.children())[:-1]
        )
                # Freezing ResNet50 weights
        for param in self.backbone.parameters():
        param.requires_grad = False
        
        # Embedding Layer
        

        self.embedding = nn.Sequential(

            nn.Linear(
                2048,
                512
            ),

            nn.ReLU(),

            nn.Dropout(
                0.3
            ),

            nn.Linear(
                512,
                128
            )
        )

   
    # Single Branch
    

    def forward_once(
        self,
        x
    ):

        x = self.backbone(x)

        x = x.view(
            x.size(0),
            -1
        )

        x = self.embedding(x)
        x = nn.functional.normalize(
        x,
        p=2,
        dim=1
    )
        
        return x

   
    # Dual Branch
   
    def forward(
        self,
        img1,
        img2
    ):

        out1 = self.forward_once(
            img1
        )

        out2 = self.forward_once(
            img2
        )

        return out1, out2
