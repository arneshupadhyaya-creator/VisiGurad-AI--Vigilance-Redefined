import torch
import torch.nn.functional as F

from PIL import Image
from torchvision import transforms

from models.siamese import SiameseNetwork


class DocumentVerifier:

    def __init__(self):

        # ----------------------------------
        # Load Siamese Model
        # ----------------------------------

        self.model = SiameseNetwork()

        self.model.eval()

        # ----------------------------------
        # Image Transform
        # ----------------------------------

        self.transform = transforms.Compose([

            transforms.Resize((224, 224)),

            transforms.ToTensor(),

            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    # --------------------------------------
    # Load Image
    # --------------------------------------

    def load_image(self, image_path):

        image = Image.open(
            image_path
        ).convert("RGB")

        image = self.transform(
            image
        )

        image = image.unsqueeze(0)

        return image

    # --------------------------------------
    # Generate Embedding
    # --------------------------------------

    def get_embedding(self, image_path):

        image = self.load_image(
            image_path
        )

        with torch.no_grad():

            embedding = self.model.forward_once(
                image
            )

        return embedding

    # --------------------------------------
    # Euclidean Distance
    # --------------------------------------

    def distance(
        self,
        image1,
        image2
    ):

        emb1 = self.get_embedding(
            image1
        )

        emb2 = self.get_embedding(
            image2
        )

        distance = F.pairwise_distance(
            emb1,
            emb2
        )

        return float(
            distance.item()
        )

    # --------------------------------------
    # Cosine Similarity
    # --------------------------------------

    def similarity(
        self,
        image1,
        image2
    ):

        emb1 = self.get_embedding(
            image1
        )

        emb2 = self.get_embedding(
            image2
        )

        similarity = F.cosine_similarity(
            emb1,
            emb2
        )

        return float(
            similarity.item()
        )

    # --------------------------------------
    # Final Verification
    # --------------------------------------

    def verify(
        self,
        template_image,
        uploaded_image
    ):

        similarity = self.similarity(
            template_image,
            uploaded_image
        )

        distance = self.distance(
            template_image,
            uploaded_image
        )

        result = {

            "similarity": similarity,

            "distance": distance
        }

        return result