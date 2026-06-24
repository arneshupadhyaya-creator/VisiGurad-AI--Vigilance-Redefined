import torch
import torch.nn as nn

from PIL import Image

from torchvision import models
from torchvision import transforms


class ResNetFeatureExtractor:
    """Extracts 2048-dimensional document embeddings
    using a pretrained ResNet50 backbone."""

    def __init__(self):

        
        # Load pretrained ResNet50
        

        resnet = models.resnet50(
            weights=models.ResNet50_Weights.DEFAULT
        )

        
        # Remove classification layer
        

        self.model = nn.Sequential(
            *list(resnet.children())[:-1]
        )
        for param in self.model.parameters():
            param.requires_grad = False

        self.model.eval()

        
        # Image preprocessing pipeline
        

        self.transform = transforms.Compose([

            transforms.Resize((512, 512)),

            transforms.ToTensor(),

            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    
    # Load and preprocess image
    

    def preprocess(self, image_path):

        image = Image.open(
            image_path
        ).convert("RGB")

        image = self.transform(image)

        image = image.unsqueeze(0)

        return image

    
    # Extract feature vector
    

    def extract(self, image_path):

        image = self.preprocess(
            image_path
        )

        with torch.no_grad():

            features = self.model(
                image
            )

            features = features.view(
                features.size(0),
                -1
            )

        return features

    
    # Extract numpy embedding
   

    def extract_numpy(self, image_path):

        features = self.extract(
            image_path
        )

        return features.cpu().numpy()

    
    # Cosine similarity
    

    def cosine_similarity(
        self,
        image1,
        image2
    ):

        feat1 = self.extract(
            image1
        )

        feat2 = self.extract(
            image2
        )

        similarity = torch.nn.functional.cosine_similarity(
            feat1,
            feat2
        )

        return float(
            similarity.item()
        )

    
    # Euclidean distance
    

    def euclidean_distance(
        self,
        image1,
        image2
    ):

        feat1 = self.extract(
            image1
        )

        feat2 = self.extract(
            image2
        )

        distance = torch.norm(
            feat1 - feat2,
            p=2
        )

        return float(
            distance.item()
        )
