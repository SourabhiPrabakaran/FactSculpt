from typing import Optional, List, Dict
from factsculpt.features.models import EvidenceDeviationFeatures
from factsculpt.classifier.interfaces import ClassifierInterface
from factsculpt.classifier.models import (
    ClassificationCode,
    RESEARCH_CLASSIFICATION_NAMES,
    LEGACY_CLASSIFICATION_NAMES,
    ClassificationResult,
)

class RuleBasedExaggerationClassifier(ClassifierInterface):
    """
    Deterministic rule-based classifier that classifies claims into evidence shift categories.
    
    Supports two taxonomies:
    - taxonomy="research" (New Closed-World Research Taxonomy):
        C1 = UNCHANGED_FAITHFUL
        C2 = WEAKENED
        C3 = STRENGTHENED
        C4 = UNSUPPORTED_ADDITION
        C5 = MIXED
      Constructs the full shift vector first to prevent collapsing mixed cases into a single direction.
    - taxonomy="legacy" (Stage 6 prototype):
        C1 = ENTAILED
        C2 = EXAGGERATED_STRENGTHENED
        C3 = NEUTRAL_UNDER_SPECIFIED
        C4 = WEAKENED_REDUCED
        C5 = CONTRADICTED
    """

    DEFAULT_SEVERITY_WEIGHTS = {
        "role": 0.25,
        "qualifier": 0.15,
        "scope": 0.20,
        "certainty": 0.15,
        "impact": 0.15,
        "quantity": 0.10
    }

    def __init__(
        self,
        contradiction_threshold: float = 0.5,
        entailment_threshold: float = 0.5,
        abstention_threshold: float = 0.40,
        taxonomy: str = "legacy",
        severity_weights: Optional[Dict[str, float]] = None
    ):
        if not (0.0 <= contradiction_threshold <= 1.0):
            raise ValueError("contradiction_threshold must be between 0.0 and 1.0 inclusive")
        if not (0.0 <= entailment_threshold <= 1.0):
            raise ValueError("entailment_threshold must be between 0.0 and 1.0 inclusive")

        self.contradiction_threshold = contradiction_threshold
        self.entailment_threshold = entailment_threshold
        self.abstention_threshold = abstention_threshold
        self.taxonomy = taxonomy.lower()
        self.severity_weights = severity_weights or dict(self.DEFAULT_SEVERITY_WEIGHTS)

    def classify(self, features: EvidenceDeviationFeatures) -> ClassificationResult:
        if self.taxonomy == "research":
            return self._classify_research(features)
        else:
            return self._classify_legacy(features)

    def _classify_research(self, features: EvidenceDeviationFeatures) -> ClassificationResult:
        """
        Research Closed-World Taxonomy evaluation:
        1. Construct full shift vector first.
        2. Detect mixed positive and negative values for C5.
        3. Identify unsupported additions for C4.
        4. Detect unidirectional shifts (C3 strengthened, C2 weakened).
        5. Identify faithful / unchanged evidence as C1.
        """
        vec = features.shift_vector
        reasons = []

        pos_shifts = []
        neg_shifts = []

        for attr, val in vec.items():
            if val > 0.05:
                pos_shifts.append((attr, val))
                reasons.append(f"{attr} strengthened (+{val:.2f})")
            elif val < -0.05:
                neg_shifts.append((attr, val))
                reasons.append(f"{attr} weakened ({val:.2f})")

        # Calculate severity score
        total_sev = sum(self.severity_weights.get(k, 0.15) * abs(v) for k, v in vec.items())
        severity = round(min(total_sev, 1.0), 4)

        # Base confidence
        conf = round(min(features.extraction_confidence * features.alignment_confidence, 1.0), 4)

        # 1. Unsupported addition check
        if features.is_unsupported_addition:
            code = ClassificationCode.C4
            name = RESEARCH_CLASSIFICATION_NAMES[code]
            reasons = ["unsupported addition: claim not grounded in source evidence"]
            probabilities = {"C1": 0.02, "C2": 0.03, "C3": 0.05, "C4": 0.88, "C5": 0.02}
            abstain = conf < self.abstention_threshold
            return ClassificationResult(
                source_claim_id=features.source_claim_id,
                generated_claim_id=features.generated_claim_id,
                classification_code=code,
                classification_name=name,
                confidence=conf,
                reasons=reasons,
                shift_vector=vec,
                severity=0.85,
                probabilities=probabilities,
                abstain=abstain,
                attribute_agreement_score=features.attribute_agreement_score
            )

        # 2. Mixed cases: both positive and negative shifts present
        if len(pos_shifts) > 0 and len(neg_shifts) > 0:
            code = ClassificationCode.C5
            name = RESEARCH_CLASSIFICATION_NAMES[code]
            probabilities = {"C1": 0.05, "C2": 0.15, "C3": 0.15, "C4": 0.05, "C5": 0.60}
        # 3. Pure strengthening: positive shifts only
        elif len(pos_shifts) > 0 and len(neg_shifts) == 0:
            code = ClassificationCode.C3
            name = RESEARCH_CLASSIFICATION_NAMES[code]
            probabilities = {"C1": 0.05, "C2": 0.05, "C3": 0.80, "C4": 0.05, "C5": 0.05}
        # 4. Pure weakening: negative shifts only
        elif len(neg_shifts) > 0 and len(pos_shifts) == 0:
            code = ClassificationCode.C2
            name = RESEARCH_CLASSIFICATION_NAMES[code]
            probabilities = {"C1": 0.05, "C2": 0.80, "C3": 0.05, "C4": 0.05, "C5": 0.05}
        # 5. Contradiction without attribute shift
        elif features.contradiction_score >= self.contradiction_threshold:
            code = ClassificationCode.C5
            name = RESEARCH_CLASSIFICATION_NAMES[code]
            reasons = ["strong contradiction detected by NLI"]
            probabilities = {"C1": 0.05, "C2": 0.10, "C3": 0.10, "C4": 0.05, "C5": 0.70}
        # 6. Unchanged / Faithful
        else:
            code = ClassificationCode.C1
            name = RESEARCH_CLASSIFICATION_NAMES[code]
            reasons = ["faithful claim preserving evidential strength"]
            probabilities = {"C1": 0.85, "C2": 0.05, "C3": 0.05, "C4": 0.03, "C5": 0.02}

        abstain = conf < self.abstention_threshold

        return ClassificationResult(
            source_claim_id=features.source_claim_id,
            generated_claim_id=features.generated_claim_id,
            classification_code=code,
            classification_name=name,
            confidence=conf,
            reasons=reasons,
            shift_vector=vec,
            severity=severity,
            probabilities=probabilities,
            abstain=abstain,
            attribute_agreement_score=features.attribute_agreement_score
        )

    def _classify_legacy(self, features: EvidenceDeviationFeatures) -> ClassificationResult:
        """
        Legacy Stage 6 classification rules with C6 extension for unsupported additions.
        """
        # RULE 0 - C4 UNSUPPORTED ADDITION (unaligned claims)
        # Generated claims with no aligned source claim above the similarity threshold
        # route to C4 instead of defaulting to neutral NLI + C3.
        if features.is_unsupported_addition or features.source_claim_id is None:
            return ClassificationResult(
                source_claim_id=features.source_claim_id,
                generated_claim_id=features.generated_claim_id,
                classification_code=ClassificationCode.C4,
                classification_name=RESEARCH_CLASSIFICATION_NAMES[ClassificationCode.C4],
                confidence=1.0,
                reasons=["no aligned source claim found above similarity threshold"],
                shift_vector=features.shift_vector
            )

        # RULE 1 - C5 CONTRADICTION
        if features.contradiction_score >= self.contradiction_threshold:
            return ClassificationResult(
                source_claim_id=features.source_claim_id,
                generated_claim_id=features.generated_claim_id,
                classification_code=ClassificationCode.C5,
                classification_name=LEGACY_CLASSIFICATION_NAMES[ClassificationCode.C5],
                confidence=1.0,
                reasons=["strong contradiction detected by NLI"],
                shift_vector=features.shift_vector
            )

        # RULE 2 - C2 STRENGTHENING
        strengthening_reasons = []
        if features.role_strengthening:
            strengthening_reasons.append("role agency strengthened")
        if features.qualifier_strengthening:
            strengthening_reasons.append("qualifier strengthened")
        if features.scope_expansion:
            strengthening_reasons.append("scope expanded")
        if features.certainty_strengthening:
            strengthening_reasons.append("certainty strengthened")
        if features.impact_strengthening:
            strengthening_reasons.append("impact strengthened")

        if strengthening_reasons:
            return ClassificationResult(
                source_claim_id=features.source_claim_id,
                generated_claim_id=features.generated_claim_id,
                classification_code=ClassificationCode.C2,
                classification_name=LEGACY_CLASSIFICATION_NAMES[ClassificationCode.C2],
                confidence=1.0,
                reasons=strengthening_reasons,
                shift_vector=features.shift_vector
            )

        # RULE 3 - C4 WEAKENING
        weakening_reasons = []
        if features.role_weakening:
            weakening_reasons.append("role agency weakened")
        if features.qualifier_weakening:
            weakening_reasons.append("qualifier weakened")
        if features.scope_reduction:
            weakening_reasons.append("scope reduced")
        if features.certainty_weakening:
            weakening_reasons.append("certainty weakened")
        if features.impact_weakening:
            weakening_reasons.append("impact weakened")

        if weakening_reasons:
            return ClassificationResult(
                source_claim_id=features.source_claim_id,
                generated_claim_id=features.generated_claim_id,
                classification_code=ClassificationCode.C4,
                classification_name=LEGACY_CLASSIFICATION_NAMES[ClassificationCode.C4],
                confidence=1.0,
                reasons=weakening_reasons,
                shift_vector=features.shift_vector
            )

        # RULE 4 - C1 CLEAN ENTAILMENT
        has_any_strengthening = (
            features.role_strengthening
            or features.qualifier_strengthening
            or features.scope_expansion
            or features.certainty_strengthening
            or features.impact_strengthening
        )
        has_any_weakening = (
            features.role_weakening
            or features.qualifier_weakening
            or features.scope_reduction
            or features.certainty_weakening
            or features.impact_weakening
        )
        has_any_conservative_change = (
            features.quantitative_change
            or features.domain_change
            or features.activity_change
            or features.object_change
        )

        if (
            features.entailment_score >= self.entailment_threshold
            and not has_any_strengthening
            and not has_any_weakening
            and not has_any_conservative_change
        ):
            return ClassificationResult(
                source_claim_id=features.source_claim_id,
                generated_claim_id=features.generated_claim_id,
                classification_code=ClassificationCode.C1,
                classification_name=LEGACY_CLASSIFICATION_NAMES[ClassificationCode.C1],
                confidence=1.0,
                reasons=["strong entailment with no meaningful evidence deviation"],
                shift_vector=features.shift_vector
            )

        # RULE 5 - C3 NEUTRAL / FALLBACK
        # TODO: Reassess whether C3 (NEUTRAL_UNDER_SPECIFIED) should split into two classes:
        #   - C3a (NEUTRAL_SUBSTITUTION): Orthogonal attribute replacement (domain/activity/object)
        #   - C3b (UNDER_SPECIFIED): Omission of constraining detail without active negation
        # Current reasoning: Retained as unified C3 for atomic claims because attribute substitutions vs omissions
        # often lack sharp boundaries without deep ontology. Distinctly unaligned claims are now handled by C6.
        reasons = ["neutral NLI relationship with no decisive evidence deviation"]
        if features.quantitative_change:
            reasons.append("quantitative information changed")
        if features.domain_change:
            reasons.append("domain attribute changed")
        if features.activity_change:
            reasons.append("activity action changed")
        if features.object_change:
            reasons.append("object attribute changed")

        return ClassificationResult(
            source_claim_id=features.source_claim_id,
            generated_claim_id=features.generated_claim_id,
            classification_code=ClassificationCode.C3,
            classification_name=LEGACY_CLASSIFICATION_NAMES[ClassificationCode.C3],
            confidence=0.5,
            reasons=reasons,
            shift_vector=features.shift_vector
        )

# Direct alias for research rule-based classifier
class ResearchRuleBasedClassifier(RuleBasedExaggerationClassifier):
    def __init__(self, **kwargs):
        kwargs["taxonomy"] = "research"
        super().__init__(**kwargs)
