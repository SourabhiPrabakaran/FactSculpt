from abc import ABC, abstractmethod
from factsculpt.features.models import EvidenceDeviationFeatures
from factsculpt.classifier.models import ClassificationResult

class ClassifierInterface(ABC):
    """
    Abstract interface for classifying aligned claim features.
    """

    @abstractmethod
    def classify(
        self,
        features: EvidenceDeviationFeatures
    ) -> ClassificationResult:
        """
        Classifies aligned generated claim features into one of C1-C5 categories.

        Args:
            features: The EvidenceDeviationFeatures containing NLI, similarity,
                      and attribute difference features.

        Returns:
            A ClassificationResult instance.
        """
        pass
