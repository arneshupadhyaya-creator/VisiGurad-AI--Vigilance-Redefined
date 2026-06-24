import torch
import torch.nn.functional as F


class SimilarityEngine:

    @staticmethod
    def cosine_similarity(
        emb1,
        emb2
    ):
        score = F.cosine_similarity(
            emb1,
            emb2
        )

        return float(score.item())

    @staticmethod
    def euclidean_distance(
        emb1,
        emb2
    ):
        distance = F.pairwise_distance(
            emb1,
            emb2
        )

        return float(distance.item())