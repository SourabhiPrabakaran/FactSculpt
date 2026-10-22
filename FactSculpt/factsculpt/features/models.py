from typing import Optional, Dict, List
from pydantic import BaseModel, Field, field_validator, model_validator

class EvidenceDeviationFeatures(BaseModel):
    """
    Consolidated Pydantic model representing evidence deviation features
    combining alignment, NLI, and attribute-level difference deltas.
    Includes continuous signed shift vectors, magnitude metrics, agreement,
    and vector serialization for learned classifiers.
    """
    source_claim_id: Optional[str] = None
    generated_claim_id: str

    semantic_similarity: Optional[float] = None
    alignment_confidence: float = 1.0

    entailment_score: float
    neutral_score: float
    contradiction_score: float

    # Boolean indicators for transformations (backward compatible)
    role_strengthening: bool = False
    role_weakening: bool = False

    qualifier_strengthening: bool = False
    qualifier_weakening: bool = False

    scope_expansion: bool = False
    scope_reduction: bool = False

    certainty_strengthening: bool = False
    certainty_weakening: bool = False

    impact_strengthening: bool = False
    impact_weakening: bool = False

    # Boolean indicators for changes
    quantitative_change: bool = False
    domain_change: bool = False
    activity_change: bool = False
    object_change: bool = False

    # Continuous 6-attribute signed shift vector
    shift_vector: Dict[str, float] = Field(
        default_factory=lambda: {
            "role": 0.0, "qualifier": 0.0, "scope": 0.0,
            "certainty": 0.0, "impact": 0.0, "quantity": 0.0
        }
    )

    # Magnitudes & Agreement
    absolute_magnitude: Dict[str, float] = Field(default_factory=dict)
    overall_magnitude: float = 0.0
    attribute_agreement_score: float = 1.0
    extraction_confidence: float = 1.0

    # Support aggregation
    supporting_claim_count: int = 1
    max_support_similarity: float = 0.0
    is_unsupported_addition: bool = False

    # Aggregate counts
    total_strengthening_count: int = 0
    total_weakening_count: int = 0
    total_expansion_count: int = 0
    total_reduction_count: int = 0
    total_changed_attributes: int = 0

    @field_validator("generated_claim_id")
    @classmethod
    def check_non_empty_generated_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("generated_claim_id cannot be empty or whitespace-only")
        return v.strip()

    @field_validator("entailment_score", "neutral_score", "contradiction_score")
    @classmethod
    def check_probability_range(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Probability scores must be between 0.0 and 1.0 inclusive")
        return v

    @field_validator("semantic_similarity")
    @classmethod
    def check_similarity_range(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (-1.0 <= v <= 1.0):
            raise ValueError("semantic_similarity must be between -1.0 and 1.0 inclusive")
        return v

    @model_validator(mode="after")
    def validate_probability_distribution(self) -> "EvidenceDeviationFeatures":
        total = self.entailment_score + self.neutral_score + self.contradiction_score
        # Enforce sum to be within +/- 0.001 tolerance of 1.0
        if not (0.999 <= total <= 1.001):
            raise ValueError(f"Scores must sum to approximately 1.0 (got {total})")
        return self

    @field_validator(
        "total_strengthening_count",
        "total_weakening_count",
        "total_expansion_count",
        "total_reduction_count",
        "total_changed_attributes",
    )
    @classmethod
    def check_non_negative_counts(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Aggregate counts cannot be negative")
        return v

    def to_feature_vector(self) -> List[float]:
        """
        Converts the feature payload into a fixed-length numeric vector
        for learned scikit-learn models (LogReg, GBDT).
        """
        vec = self.shift_vector
        sim = self.semantic_similarity if self.semantic_similarity is not None else 0.0
        return [
            self.entailment_score,
            self.neutral_score,
            self.contradiction_score,
            sim,
            self.alignment_confidence,
            self.extraction_confidence,
            vec.get("role", 0.0),
            vec.get("qualifier", 0.0),
            vec.get("scope", 0.0),
            vec.get("certainty", 0.0),
            vec.get("impact", 0.0),
            vec.get("quantity", 0.0),
            self.overall_magnitude,
            self.attribute_agreement_score,
            float(self.total_strengthening_count),
            float(self.total_weakening_count),
            float(self.total_changed_attributes),
            float(self.supporting_claim_count),
            1.0 if self.is_unsupported_addition else 0.0
        ]
