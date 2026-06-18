import torch
import torch.nn as nn
import torch.nn.functional as F


class ContrastiveLoss(nn.Module):
    def __init__(self, margin=2.0):
        super().__init__()
        self.margin = margin

    def forward(self, output1, output2, label):
        distance = F.pairwise_distance(output1, output2)

        positive_loss = (1 - label) * distance.pow(2)

        negative_loss = label * (
            torch.clamp(self.margin - distance, min=0.0).pow(2)
        )

        loss = torch.mean(positive_loss + negative_loss)

        return loss
