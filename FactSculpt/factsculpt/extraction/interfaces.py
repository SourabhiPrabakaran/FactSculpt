from abc import ABC, abstractmethod
from typing import List, Optional
from factsculpt.models import AtomicClaim, EvidenceProfile

class AtomicClaimExtractor(ABC):
    """
    Abstract interface for extracting atomic claims from text.
    Must preserve claim provenance and assign unique IDs to each claim.
    """

    @abstractmethod
    def extract_claims(self, text: str) -> List[AtomicClaim]:
        """
        Extracts atomic claims from the given text block.

        Args:
            text: The text block (source or generated) to extract from.

        Returns:
            A list of AtomicClaim models, containing unique IDs, the claim text,
            and character span indices mapping back to the input text.
        """
        pass

class EvidenceProfileExtractor(ABC):
    """
    Abstract interface for extracting a structured evidence profile from a single atomic claim.
    """

    @abstractmethod
    def extract_profile(self, claim: AtomicClaim) -> EvidenceProfile:
        """
        Extracts semantic attributes (role, qualifier, etc.) from an atomic claim.

        Args:
            claim: The AtomicClaim to analyze.

        Returns:
            An EvidenceProfile containing the extracted attributes, where
            unspecified/non-present features are set to None.
        """
        pass
