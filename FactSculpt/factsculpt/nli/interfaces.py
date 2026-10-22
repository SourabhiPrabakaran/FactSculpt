from abc import ABC, abstractmethod
from factsculpt.nli.models import NLIResult

class NLIClassifier(ABC):
    """
    Abstract interface for Natural Language Inference classification.
    
    Interpretation:
    - premise = SOURCE CLAIM
    - hypothesis = GENERATED CLAIM
    """

    @abstractmethod
    def predict(
        self,
        premise: str,
        hypothesis: str
    ) -> NLIResult:
        """
        Predicts the NLI relationship between premise (source claim) and hypothesis (generated claim).

        Args:
            premise: The reference statement (Source Claim text).
            hypothesis: The proposed statement (Generated Claim text).

        Returns:
            An NLIResult containing scores for ENTAILMENT, NEUTRAL, and CONTRADICTION.
        """
        pass
