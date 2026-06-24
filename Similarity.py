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

    @staticmethod
    def structural_score(cosine_score):

        return round(
            cosine_score * 100,
            2
        )

    @staticmethod
    def confidence_score(cosine_score):

        confidence = max(
            0,
            min(cosine_score * 100, 99.9)
        )

        return round(
            confidence,
            2

    @staticmethod
    def verdict(cosine_score):

        if cosine_score >= 0.90:
            return "AUTHENTIC"

        elif cosine_score >= 0.75:
            return "SUSPICIOUS"

        else:
            return "POSSIBLE FORGERY" 
    
    
            
            
    
