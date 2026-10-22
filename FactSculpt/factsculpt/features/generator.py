import math
from typing import Optional, Dict, Any
from factsculpt.nli.models import EvidenceAnalysisResult
from factsculpt.differencing.models import ChangeType, Direction
from factsculpt.features.interfaces import EvidenceFeatureGenerator
from factsculpt.features.models import EvidenceDeviationFeatures

class EvidenceDeviationFeatureGenerator(EvidenceFeatureGenerator):
    """
    Deterministic feature generator that computes:
    - 6-attribute continuous signed shift vector
    - Absolute and overall magnitudes
    - Directional agreement score
    - NLI probability scores
    - Alignment and extraction confidences
    - Support aggregation features
    - Legacy boolean flags for backward compatibility
    """

    def generate(
        self,
        analysis: EvidenceAnalysisResult,
        semantic_similarity: Optional[float] = None,
        extraction_confidence: float = 1.0,
        alignment_confidence: float = 1.0,
        supporting_claim_count: int = 1,
        is_unsupported_addition: bool = False
    ) -> EvidenceDeviationFeatures:
        nli = analysis.nli_result
        diff = analysis.attribute_difference

        # Initialize boolean indicators
        role_strengthening = False
        role_weakening = False
        qualifier_strengthening = False
        qualifier_weakening = False
        scope_expansion = False
        scope_reduction = False
        certainty_strengthening = False
        certainty_weakening = False
        impact_strengthening = False
        impact_weakening = False

        quantitative_change = False
        domain_change = False
        activity_change = False
        object_change = False

        # Initialize aggregate counts
        total_strengthening_count = 0
        total_weakening_count = 0
        total_expansion_count = 0
        total_reduction_count = 0
        total_changed_attributes = 0

        # Traverse and map all deltas
        for delta in diff.deltas:
            attr = delta.attribute_name
            ctype = delta.change_type
            direction = delta.direction

            if ctype != ChangeType.UNCHANGED:
                total_changed_attributes += 1

            if direction == Direction.STRENGTHENED:
                total_strengthening_count += 1
            elif direction == Direction.WEAKENED:
                total_weakening_count += 1
            elif direction == Direction.EXPANDED:
                total_expansion_count += 1
            elif direction == Direction.REDUCED:
                total_reduction_count += 1

            # Map specific indicators
            if attr == "role_agency":
                if direction == Direction.STRENGTHENED:
                    role_strengthening = True
                elif direction == Direction.WEAKENED:
                    role_weakening = True
            elif attr == "qualifier":
                if direction == Direction.STRENGTHENED:
                    qualifier_strengthening = True
                elif direction == Direction.WEAKENED:
                    qualifier_weakening = True
            elif attr == "scope":
                if direction == Direction.EXPANDED:
                    scope_expansion = True
                elif direction == Direction.REDUCED:
                    scope_reduction = True
            elif attr == "certainty":
                if direction == Direction.STRENGTHENED:
                    certainty_strengthening = True
                elif direction == Direction.WEAKENED:
                    certainty_weakening = True
            elif attr == "impact":
                if direction == Direction.STRENGTHENED:
                    impact_strengthening = True
                elif direction == Direction.WEAKENED:
                    impact_weakening = True
            elif attr == "quantitative_info":
                if ctype != ChangeType.UNCHANGED:
                    quantitative_change = True
            elif attr == "domain":
                if ctype != ChangeType.UNCHANGED:
                    domain_change = True
            elif attr == "activity_action":
                if ctype != ChangeType.UNCHANGED:
                    activity_change = True
            elif attr == "object":
                if ctype != ChangeType.UNCHANGED:
                    object_change = True

        # Extract or compute shift vector
        if hasattr(diff, "shift_vector") and diff.shift_vector:
            shift_vector = dict(diff.shift_vector)
        else:
            shift_vector = {
                "role": 1.0 if role_strengthening else (-1.0 if role_weakening else 0.0),
                "qualifier": 1.0 if qualifier_strengthening else (-1.0 if qualifier_weakening else 0.0),
                "scope": 1.0 if scope_expansion else (-1.0 if scope_reduction else 0.0),
                "certainty": 1.0 if certainty_strengthening else (-1.0 if certainty_weakening else 0.0),
                "impact": 1.0 if impact_strengthening else (-1.0 if impact_weakening else 0.0),
                "quantity": 0.5 if quantitative_change else 0.0,
            }

        # Absolute magnitudes
        absolute_magnitude = {k: round(abs(v), 4) for k, v in shift_vector.items()}
        overall_magnitude = round(sum(absolute_magnitude.values()), 4)

        # Attribute agreement score
        pos_shifts = sum(1 for v in shift_vector.values() if v > 0.05)
        neg_shifts = sum(1 for v in shift_vector.values() if v < -0.05)
        total_active_shifts = pos_shifts + neg_shifts

        if total_active_shifts == 0:
            agreement_score = 1.0
        elif pos_shifts > 0 and neg_shifts > 0:
            agreement_score = round(max(pos_shifts, neg_shifts) / total_active_shifts, 4)
        else:
            agreement_score = 1.0

        return EvidenceDeviationFeatures(
            source_claim_id=analysis.source_claim_id,
            generated_claim_id=analysis.generated_claim_id,
            semantic_similarity=semantic_similarity,
            alignment_confidence=alignment_confidence,
            entailment_score=nli.entailment_score,
            neutral_score=nli.neutral_score,
            contradiction_score=nli.contradiction_score,
            role_strengthening=role_strengthening,
            role_weakening=role_weakening,
            qualifier_strengthening=qualifier_strengthening,
            qualifier_weakening=qualifier_weakening,
            scope_expansion=scope_expansion,
            scope_reduction=scope_reduction,
            certainty_strengthening=certainty_strengthening,
            certainty_weakening=certainty_weakening,
            impact_strengthening=impact_strengthening,
            impact_weakening=impact_weakening,
            quantitative_change=quantitative_change,
            domain_change=domain_change,
            activity_change=activity_change,
            object_change=object_change,
            shift_vector=shift_vector,
            absolute_magnitude=absolute_magnitude,
            overall_magnitude=overall_magnitude,
            attribute_agreement_score=agreement_score,
            extraction_confidence=extraction_confidence,
            supporting_claim_count=supporting_claim_count,
            max_support_similarity=semantic_similarity if semantic_similarity is not None else 0.0,
            is_unsupported_addition=is_unsupported_addition,
            total_strengthening_count=total_strengthening_count,
            total_weakening_count=total_weakening_count,
            total_expansion_count=total_expansion_count,
            total_reduction_count=total_reduction_count,
            total_changed_attributes=total_changed_attributes,
        )
