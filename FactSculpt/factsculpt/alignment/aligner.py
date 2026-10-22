from typing import List, Optional, Any
from factsculpt.models import AtomicClaim
from factsculpt.config import FactSculptConfig
from factsculpt.alignment.interfaces import ClaimAligner, EmbeddingGenerator
from factsculpt.alignment.models import ClaimAlignment, AlignmentResult, SupportType
from factsculpt.alignment.cosine import cosine_similarity

class EmbeddingClaimAligner(ClaimAligner):
    """
    Enhanced semantic claim aligner supporting:
    - Many-to-one alignment (multiple source claims jointly supporting a generated claim)
    - NLI-based reranking when an NLI classifier is provided
    - Explicit detection and flagging of UNSUPPORTED_ADDITION claims
    """

    def __init__(
        self,
        embedding_generator: EmbeddingGenerator,
        config: Optional[FactSculptConfig] = None,
        nli_classifier: Optional[Any] = None,
        enable_many_to_one: bool = True,
        many_to_one_threshold: float = 0.55
    ):
        self.embedding_generator = embedding_generator
        self.config = config or FactSculptConfig()
        self.nli_classifier = nli_classifier
        self.enable_many_to_one = enable_many_to_one
        self.many_to_one_threshold = many_to_one_threshold

    def align(
        self,
        source_claims: List[AtomicClaim],
        generated_claims: List[AtomicClaim],
        threshold: Optional[float] = None,
    ) -> AlignmentResult:
        threshold_to_use = threshold if threshold is not None else self.config.similarity_threshold

        if not generated_claims:
            return AlignmentResult(alignments=[], unsupported_claim_ids=[])

        gen_texts = [claim.text for claim in generated_claims]
        gen_embeddings = self.embedding_generator.get_embeddings(gen_texts)

        # Handle empty source claims list (all generated claims are unsupported)
        if not source_claims:
            alignments = []
            unsupported = []
            for claim in generated_claims:
                unsupported.append(claim.claim_id)
                alignments.append(
                    ClaimAlignment(
                        source_claim_id=None,
                        source_claim_ids=[],
                        generated_claim_id=claim.claim_id,
                        similarity_score=0.0,
                        alignment_score=0.0,
                        threshold_used=threshold_to_use,
                        support_type=SupportType.UNSUPPORTED_ADDITION,
                        is_match=False
                    )
                )
            return AlignmentResult(alignments=alignments, unsupported_claim_ids=unsupported)

        # Generate embeddings for all source claims
        src_texts = [claim.text for claim in source_claims]
        src_embeddings = self.embedding_generator.get_embeddings(src_texts)

        alignments = []
        unsupported_ids = []

        for i, gen_claim in enumerate(generated_claims):
            gen_emb = gen_embeddings[i]

            # Compute similarities against all source claims
            candidate_scores = []
            for j, src_claim in enumerate(source_claims):
                score = cosine_similarity(gen_emb, src_embeddings[j])
                candidate_scores.append((src_claim, score))

            # Sort descending by cosine similarity
            candidate_scores.sort(key=lambda x: x[1], reverse=True)
            best_src, best_score = candidate_scores[0]

            # NLI Reranking if available
            if self.nli_classifier is not None and hasattr(self.nli_classifier, "predict"):
                reranked_candidates = []
                for src_c, cos_s in candidate_scores[:3]:
                    try:
                        nli_res = self.nli_classifier.predict(src_c.text, gen_claim.text)
                        # Blended score: 0.5 * cosine + 0.5 * entailment
                        combined = 0.5 * max(cos_s, 0.0) + 0.5 * nli_res.entailment_score
                        reranked_candidates.append((src_c, combined, cos_s))
                    except Exception:
                        reranked_candidates.append((src_c, cos_s, cos_s))

                reranked_candidates.sort(key=lambda x: x[1], reverse=True)
                best_src, best_combined, best_score = reranked_candidates[0]
            else:
                best_combined = best_score

            is_match = best_combined >= threshold_to_use

            if not is_match:
                # Unsupported addition
                unsupported_ids.append(gen_claim.claim_id)
                alignments.append(
                    ClaimAlignment(
                        source_claim_id=best_src.claim_id,
                        source_claim_ids=[best_src.claim_id],
                        generated_claim_id=gen_claim.claim_id,
                        similarity_score=best_score,
                        alignment_score=best_combined,
                        threshold_used=threshold_to_use,
                        support_type=SupportType.UNSUPPORTED_ADDITION,
                        is_match=False
                    )
                )

            else:
                # Check for Many-to-One Alignment
                # Multiple source claims whose similarity exceeds many_to_one_threshold
                supporting_ids = [best_src.claim_id]

                if self.enable_many_to_one:
                    for s_claim, s_score in candidate_scores[1:]:
                        if s_score >= self.many_to_one_threshold and s_claim.claim_id not in supporting_ids:
                            supporting_ids.append(s_claim.claim_id)

                if len(supporting_ids) > 1:
                    supp_type = SupportType.MANY_TO_ONE
                elif best_score >= 0.95:
                    supp_type = SupportType.EXACT_MATCH
                else:
                    supp_type = SupportType.DIRECT_SUPPORT

                alignments.append(
                    ClaimAlignment(
                        source_claim_id=best_src.claim_id,
                        source_claim_ids=supporting_ids,
                        generated_claim_id=gen_claim.claim_id,
                        similarity_score=best_score,
                        alignment_score=best_combined,
                        threshold_used=threshold_to_use,
                        support_type=supp_type,
                        is_match=True
                    )
                )

        return AlignmentResult(alignments=alignments, unsupported_claim_ids=unsupported_ids)
