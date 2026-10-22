from abc import ABC, abstractmethod
from typing import List, Optional
from factsculpt.models import AtomicClaim
from factsculpt.alignment.models import AlignmentResult

class EmbeddingGenerator(ABC):
    """
    Abstract interface for generating semantic vector embeddings from texts.
    """

    @abstractmethod
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates semantic embeddings for a list of strings.

        Args:
            texts: List of text strings to embed.

        Returns:
            A list of float lists representing embedding vectors.
        """
        pass

class ClaimAligner(ABC):
    """
    Abstract interface for semantically aligning generated claims to source claims.
    """

    @abstractmethod
    def align(
        self,
        source_claims: List[AtomicClaim],
        generated_claims: List[AtomicClaim],
        threshold: Optional[float] = None,
    ) -> AlignmentResult:
        """
        Aligns a set of generated claims to a set of source claims.

        Args:
            source_claims: List of source AtomicClaims.
            generated_claims: List of generated AtomicClaims.
            threshold: Optional threshold override.

        Returns:
            An AlignmentResult containing ClaimAlignment records.
        """
        pass
