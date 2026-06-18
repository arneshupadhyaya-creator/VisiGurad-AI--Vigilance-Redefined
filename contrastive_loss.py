import torch
import torch.nn as nn
import torch.nn.functional as F


class ContrastiveLoss(nn.Module):

    def __init__(
        self,
        margin=2.0
    ):

        super().__init__()

        self.margin = margin

    def forward(
        self,
        output1,
        output2,
        label
    ):

        distance = F.pairwise_distance(
            output1,
            output2
        )

        loss = torch.mean(

            (1 - label)
            * torch.pow(
                distance,
                2
            )

            +

            label
            * torch.pow(

                torch.clamp(
                    self.margin
                    - distance,
                    min=0.0
                ),

                2
            )
        )

        return loss