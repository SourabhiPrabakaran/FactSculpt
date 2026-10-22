from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from factsculpt.differencing.models import AttributeDifferenceResult

class NLILabel(str, Enum):
    """
    Standard natural language inference labels.
    """
    ENTAILMENT = "ENTAILMENT"
    NEUTRAL = "NEUTRAL"
    CONTRADICTION = "CONTRADICTION"

class NLIResult(BaseModel):
    """
    Structured outcome of NLI evaluation between premise and hypothesis.
    """
    source_claim_id: Optional[str] = None
    generated_claim_id: str
    label: NLILabel
    entailment_score: float = Field(..., description="Probability of Entailment in [0, 1]")
    neutral_score: float = Field(..., description="Probability of Neutral in [0, 1]")
    contradiction_score: float = Field(..., description="Probability of Contradiction in [0, 1]")
    model_name: str

    @field_validator("generated_claim_id", "model_name")
    @classmethod
    def check_non_empty_strings(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace-only")
        return v.strip()

    @field_validator("entailment_score", "neutral_score", "contradiction_score")
    @classmethod
    def check_score_range(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("NLI probability scores must be between 0.0 and 1.0 inclusive")
        return v

    @model_validator(mode="after")
    def validate_probability_distribution(self) -> "NLIResult":
        total = self.entailment_score + self.neutral_score + self.contradiction_score
        # Check sum with a tolerance of +/- 0.001
        if not (0.999 <= total <= 1.001):
            raise ValueError(f"NLI probability scores must sum to approximately 1.0 (got {total})")
        return self

class EvidenceAnalysisResult(BaseModel):
    """
    Analyzed evidence package combining semantic alignment, NLI, and attribute difference results.
    """
    source_claim_id: Optional[str] = None
    generated_claim_id: str
    nli_result: NLIResult
    attribute_difference: AttributeDifferenceResult

    @field_validator("generated_claim_id")
    @classmethod
    def check_non_empty_generated_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("generated_claim_id cannot be empty or whitespace-only")
        return v.strip()
