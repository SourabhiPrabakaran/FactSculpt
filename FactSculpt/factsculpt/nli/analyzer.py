from factsculpt.models import AtomicClaim
from factsculpt.nli.interfaces import NLIClassifier
from factsculpt.differencing.interfaces import AttributeDifferencer
from factsculpt.nli.models import EvidenceAnalysisResult

class EvidenceAnalyzer:
    """
    Coordinates semantic/structural NLI inference and attribute differencing
    to evaluate deviations between aligned source and generated claims.
    """

    def __init__(self, nli_classifier: NLIClassifier, differencer: AttributeDifferencer):
        self.nli_classifier = nli_classifier
        self.differencer = differencer

    def analyze(
        self,
        source_claim: AtomicClaim,
        generated_claim: AtomicClaim
    ) -> EvidenceAnalysisResult:
        # Run NLI classification
        # Premise = Source Claim Text
        # Hypothesis = Generated Claim Text
        nli_res = self.nli_classifier.predict(
            premise=source_claim.text,
            hypothesis=generated_claim.text
        )

        # Update IDs on the NLIResult to align provenance
        nli_res.source_claim_id = source_claim.claim_id
        nli_res.generated_claim_id = generated_claim.claim_id

        # Run Stage 3 attribute differencer
        diff_res = self.differencer.compare(source_claim, generated_claim)

        # Combine NLI Result and Attribute Differencing Result into EvidenceAnalysisResult
        return EvidenceAnalysisResult(
            source_claim_id=source_claim.claim_id,
            generated_claim_id=generated_claim.claim_id,
            nli_result=nli_res,
            attribute_difference=diff_res
        )
