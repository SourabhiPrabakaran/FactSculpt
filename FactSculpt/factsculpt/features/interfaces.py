from abc import ABC, abstractmethod
from typing import Optional
from factsculpt.nli.models import EvidenceAnalysisResult
from factsculpt.features.models import EvidenceDeviationFeatures

class EvidenceFeatureGenerator(ABC):
    """
    Abstract interface for generating structured evidence-deviation features from analysis results.
    """

    @abstractmethod
    def generate(
        self,
        analysis: EvidenceAnalysisResult,
        semantic_similarity: Optional[float] = None
    ) -> EvidenceDeviationFeatures:
        """
        Transforms EvidenceAnalysisResult and semantic similarity into consolidated features.

        Args:
            analysis: The EvidenceAnalysisResult containing NLI result and attribute deltas.
            semantic_similarity: Optional cosine similarity score from alignment.

        Returns:
            An EvidenceDeviationFeatures model instance.
        """
        pass
