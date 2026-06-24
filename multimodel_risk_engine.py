class MultiModalRiskEngine:

    def __init__(self):

        self.weights = {

            "forensic": 0.35,

            "structural": 0.45,

            "behavioral": 0.20
        }

    # ----------------------------------
    # Master Trust Score
    # ----------------------------------

    def calculate_trust_score(

        self,

        forensic_score,

        structural_score,

        behavioral_score

    ):

        trust_score = (

            forensic_score
            * self.weights["forensic"]

            +

            structural_score
            * self.weights["structural"]

            +

            behavioral_score
            * self.weights["behavioral"]

        )

        return round(
            trust_score,
            2
        )

    # ----------------------------------
    # Final Decision
    # ----------------------------------

    def classify(
        self,
        trust_score
    ):

        if trust_score >= 80:

            return "LOW RISK"

        elif trust_score >= 60:

            return "MANUAL REVIEW"

        else:

            return "HIGH RISK"

    # ----------------------------------
    # Full Evaluation
    # ----------------------------------

    def evaluate(

        self,

        forensic_score,

        structural_score,

        behavioral_score

    ):

        trust_score = self.calculate_trust_score(

            forensic_score,

            structural_score,

            behavioral_score

        )

        verdict = self.classify(
            trust_score
        )

        return {

            "forensic_score":
            forensic_score,

            "structural_score":
            structural_score,

            "behavioral_score":
            behavioral_score,

            "master_trust_score":
            trust_score,

            "verdict":
            verdict
        }