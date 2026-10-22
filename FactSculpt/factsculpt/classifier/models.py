from typing import List, Optional, Dict
from pydantic import BaseModel, Field, field_validator, model_validator
from factsculpt.taxonomy import (
    ClaimTaxonomy,
    ClassificationCode,
    TAXONOMY_NAMES,
    RESEARCH_CLASSIFICATION_NAMES,
    LEGACY_CLASSIFICATION_NAMES
)

CLASSIFICATION_NAMES = RESEARCH_CLASSIFICATION_NAMES

class ClassificationResult(BaseModel):
    """
    Output structure representing the exaggeration classification outcome.
    Includes continuous shift vector, severity, probabilities, calibration, and abstention.
    """
    source_claim_id: Optional[str] = None
    generated_claim_id: str
    classification_code: ClassificationCode
    classification_name: str
    confidence: float
    reasons: List[str] = Field(default_factory=list)
    shift_vector: Dict[str, float] = Field(default_factory=dict)
    severity: float = 0.0
    probabilities: Dict[str, float] = Field(default_factory=dict)
    abstain: bool = False
    attribute_agreement_score: float = 1.0

    @field_validator("generated_claim_id")
    @classmethod
    def clean_claim_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("generated_claim_id cannot be empty or whitespace-only")
        return v.strip()

    @field_validator("confidence")
    @classmethod
    def check_confidence_range(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("confidence must be between 0.0 and 1.0 inclusive")
        return v

    @model_validator(mode="after")
    def validate_code_name_consistency(self) -> "ClassificationResult":
        expected_research = RESEARCH_CLASSIFICATION_NAMES.get(self.classification_code)
        expected_legacy = LEGACY_CLASSIFICATION_NAMES.get(self.classification_code)
        if self.classification_name not in (expected_research, expected_legacy):
            raise ValueError(
                f"Inconsistent classification: code '{self.classification_code}' "
                f"does not match name '{self.classification_name}' "
                f"(expected '{expected_research}' or '{expected_legacy}')"
            )
        return self
