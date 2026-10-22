from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from factsculpt.config import FactSculptConfig
from factsculpt.extraction.interfaces import AtomicClaimExtractor, EvidenceProfileExtractor
from factsculpt.extraction.mock import MockAtomicClaimExtractor, MockEvidenceProfileExtractor
from factsculpt.alignment.interfaces import ClaimAligner, EmbeddingGenerator
from factsculpt.differencing.interfaces import AttributeDifferencer
from factsculpt.differencing.engine import AttributeDifferenceEngine
from factsculpt.differencing.models import AttributeDifferenceResult, ProfileStatus
from factsculpt.nli.interfaces import NLIClassifier
from factsculpt.nli.models import NLIResult, NLILabel, EvidenceAnalysisResult
from factsculpt.features.interfaces import EvidenceFeatureGenerator
from factsculpt.features.generator import EvidenceDeviationFeatureGenerator
from factsculpt.features.models import EvidenceDeviationFeatures
from factsculpt.classifier.interfaces import ClassifierInterface
from factsculpt.classifier.rules import RuleBasedExaggerationClassifier
from factsculpt.classifier.models import ClassificationResult

class PipelineResultItem(BaseModel):
    """
    Evaluation metrics and classifications for a single generated claim.
    """
    generated_claim_text: str
    source_claim_text: Optional[str] = None
    semantic_similarity: Optional[float] = None
    alignment: Any = None
    difference: AttributeDifferenceResult
    nli: NLIResult
    features: EvidenceDeviationFeatures
    classification: ClassificationResult

class PipelineResult(BaseModel):
    """
    Aggregated pipeline outcomes mapping source and generated claims.
    """
    source_claims_count: int
    generated_claims_count: int
    aligned_count: int
    unaligned_count: int
    classification_counts: Dict[str, int]
    items: List[PipelineResultItem]

class FACTSculptPipeline:
    """
    High-level orchestrator integrating FACTSculpt Stages 1-6 sequentially.
    Supports dependency injection and lazy-loads expensive NLP model weights.
    """

    def __init__(
        self,
        config: Optional[FactSculptConfig] = None,
        claim_extractor: Optional[AtomicClaimExtractor] = None,
        profile_extractor: Optional[EvidenceProfileExtractor] = None,
        embedding_generator: Optional[EmbeddingGenerator] = None,
        claim_aligner: Optional[ClaimAligner] = None,
        nli_classifier: Optional[NLIClassifier] = None,
        differencer: Optional[AttributeDifferencer] = None,
        feature_generator: Optional[EvidenceFeatureGenerator] = None,
        classifier: Optional[ClassifierInterface] = None,
    ):
        self.config = config or FactSculptConfig()
        
        # Injectable components (none default initialized at import)
        self.claim_extractor = claim_extractor
        self.profile_extractor = profile_extractor
        self.embedding_generator = embedding_generator
        self.claim_aligner = claim_aligner
        self.nli_classifier = nli_classifier
        self.differencer = differencer
        self.feature_generator = feature_generator
        self.classifier = classifier

    def _lazy_init(self):
        """
        Lazily instantiates default classifiers to keep start-up model-free.
        """
        if self.claim_extractor is None:
            self.claim_extractor = MockAtomicClaimExtractor()
        if self.profile_extractor is None:
            self.profile_extractor = MockEvidenceProfileExtractor()
        if self.differencer is None:
            self.differencer = AttributeDifferenceEngine()
        if self.feature_generator is None:
            self.feature_generator = EvidenceDeviationFeatureGenerator()
        if self.classifier is None:
            self.classifier = RuleBasedExaggerationClassifier()

        # Lazy load expensive NLP components
        if self.embedding_generator is None:
            from factsculpt.alignment.embeddings import SentenceTransformerEmbeddingGenerator
            self.embedding_generator = SentenceTransformerEmbeddingGenerator(model_name=self.config.embedding_model)
        if self.claim_aligner is None:
            from factsculpt.alignment.aligner import EmbeddingClaimAligner
            self.claim_aligner = EmbeddingClaimAligner(self.embedding_generator, config=self.config)
        if self.nli_classifier is None:
            from factsculpt.nli.models_hf import HuggingFaceNLIClassifier
            self.nli_classifier = HuggingFaceNLIClassifier(model_name=self.config.nli_model)

    def analyze(self, source_text: str, generated_text: str) -> PipelineResult:
        """
        Runs the full end-to-end evaluation pipeline.

        Args:
            source_text: Paste/load source reference text.
            generated_text: Paste/load generated AI text.

        Returns:
            A PipelineResult containing claim breakdowns and metrics.
        """
        if source_text is None or not source_text.strip():
            raise ValueError("source_text cannot be empty or whitespace-only")
        if generated_text is None or not generated_text.strip():
            raise ValueError("generated_text cannot be empty or whitespace-only")

        self._lazy_init()

        # Step 1: Extract and profile claims
        src_claims = self.claim_extractor.extract_claims(source_text)
        for c in src_claims:
            c.source_text_id = "src_doc"
            c.profile = self.profile_extractor.extract_profile(c)

        gen_claims = self.claim_extractor.extract_claims(generated_text)
        for c in gen_claims:
            c.source_text_id = "gen_doc"
            c.profile = self.profile_extractor.extract_profile(c)

        # Step 2: Claim Alignment
        alignment_res = self.claim_aligner.align(src_claims, gen_claims)

        items = []
        aligned_count = 0
        unaligned_count = 0
        classification_counts = {"C1": 0, "C2": 0, "C3": 0, "C4": 0, "C5": 0, "C6": 0}

        for gen_claim in gen_claims:
            # Locate corresponding alignment record
            align = next((a for a in alignment_res.alignments if a.generated_claim_id == gen_claim.claim_id), None)
            
            is_aligned = False
            src_claim = None

            if align and align.is_match and align.source_claim_id:
                src_claim = next((c for c in src_claims if c.claim_id == align.source_claim_id), None)
                if src_claim:
                    is_aligned = True

            if is_aligned and src_claim:
                aligned_count += 1
                
                # Step 3: Attribute Differencing
                diff = self.differencer.compare(src_claim, gen_claim)
                
                # Step 4: NLI Analysis
                nli = self.nli_classifier.predict(src_claim.text, gen_claim.text)
                nli.source_claim_id = src_claim.claim_id
                nli.generated_claim_id = gen_claim.claim_id
                
                similarity = align.similarity_score if align else None
            else:
                unaligned_count += 1
                
                # Step 3/4 defaults for unaligned claims
                diff = AttributeDifferenceResult(
                    source_claim_id=None,
                    generated_claim_id=gen_claim.claim_id,
                    profile_status=ProfileStatus.PROFILE_MISSING_SOURCE,
                    deltas=[]
                )
                nli = NLIResult(
                    source_claim_id=None,
                    generated_claim_id=gen_claim.claim_id,
                    label=NLILabel.NEUTRAL,
                    entailment_score=0.0,
                    neutral_score=1.0,
                    contradiction_score=0.0,
                    model_name="N/A"
                )
                similarity = None

            # Combined NLI & Difference payload
            analysis = EvidenceAnalysisResult(
                source_claim_id=src_claim.claim_id if src_claim else None,
                generated_claim_id=gen_claim.claim_id,
                nli_result=nli,
                attribute_difference=diff
            )

            # Step 5: Feature Generation (preserves similarity score and unsupported addition flag)
            features = self.feature_generator.generate(
                analysis,
                semantic_similarity=similarity,
                is_unsupported_addition=(not is_aligned)
            )

            # Step 6: Classification
            classification = self.classifier.classify(features)

            # Post-process unaligned classification reasons
            if not is_aligned:
                classification.reasons = ["no aligned source claim found"]

            classification_counts[classification.classification_code.value] += 1

            items.append(
                PipelineResultItem(
                    generated_claim_text=gen_claim.text,
                    source_claim_text=src_claim.text if src_claim else None,
                    semantic_similarity=similarity,
                    alignment=align,
                    difference=diff,
                    nli=nli,
                    features=features,
                    classification=classification
                )
            )

        return PipelineResult(
            source_claims_count=len(src_claims),
            generated_claims_count=len(gen_claims),
            aligned_count=aligned_count,
            unaligned_count=unaligned_count,
            classification_counts=classification_counts,
            items=items
        )
