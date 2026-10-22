from abc import ABC, abstractmethod
from factsculpt.models import AtomicClaim
from factsculpt.differencing.models import AttributeDifferenceResult

class AttributeDifferencer(ABC):
    """
    Abstract base class for comparing the structured EvidenceProfile attributes
    of aligned source and generated claims.
    """

    @abstractmethod
    def compare(
        self,
        source_claim: AtomicClaim,
        generated_claim: AtomicClaim
    ) -> AttributeDifferenceResult:
        """
        Compares the EvidenceProfile of a source claim and a generated claim.

        Args:
            source_claim: The source AtomicClaim.
            generated_claim: The generated AtomicClaim.

        Returns:
            An AttributeDifferenceResult detailing the attribute deltas.
        """
        pass
