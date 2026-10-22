from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

class SupportType(str, Enum):
    EXACT_MATCH = "EXACT_MATCH"
    DIRECT_SUPPORT = "DIRECT_SUPPORT"
    MANY_TO_ONE = "MANY_TO_ONE"
    PARTIAL_SUPPORT = "PARTIAL_SUPPORT"
    UNSUPPORTED_ADDITION = "UNSUPPORTED_ADDITION"

class ClaimAlignment(BaseModel):
    """
    Represents semantic alignment between a generated claim and one or more source claims.
    Supports 1-to-1, many-to-one alignment, and explicit unsupported additions.
    """
    source_claim_id: Optional[str] = Field(
        None,
        description="Primary source claim ID, or None if unaligned/unsupported."
    )
    source_claim_ids: List[str] = Field(
        default_factory=list,
        description="All supporting source claim IDs (supports many-to-one alignment)."
    )
    generated_claim_id: str = Field(
        ...,
        description="ID of the generated claim."
    )
    similarity_score: float = Field(
        ...,
        description="Semantic similarity score, between -1.0 and 1.0."
    )
    alignment_score: float = Field(
        0.0,
        description="Unified alignment score (cosine or NLI-reranked)."
    )
    threshold_used: float = Field(
        ...,
        description="Threshold used to determine matches."
    )
    support_type: SupportType = Field(
        SupportType.DIRECT_SUPPORT,
        description="Evidence support typology (DIRECT_SUPPORT, MANY_TO_ONE, UNSUPPORTED_ADDITION, etc.)"
    )
    is_match: bool = Field(
        ...,
        description="True if alignment satisfies the threshold, False otherwise."
    )

    @property
    def target_claim_id(self) -> str:
        return self.generated_claim_id

    @model_validator(mode="after")
    def sync_source_ids(self) -> "ClaimAlignment":
        # Keep source_claim_id and source_claim_ids in sync
        if self.source_claim_id and self.source_claim_id not in self.source_claim_ids:
            self.source_claim_ids.insert(0, self.source_claim_id)
        elif not self.source_claim_id and self.source_claim_ids:
            self.source_claim_id = self.source_claim_ids[0]
        if self.alignment_score == 0.0 and self.similarity_score != 0.0:
            self.alignment_score = self.similarity_score
        return self

    @field_validator("generated_claim_id")
    @classmethod
    def check_non_empty_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("generated_claim_id cannot be empty or whitespace-only")
        return v.strip()

    @field_validator("similarity_score", "threshold_used", "alignment_score")
    @classmethod
    def check_score_range(cls, v: float) -> float:
        if not (-1.0 <= v <= 1.0):
            raise ValueError("Score value must be between -1.0 and 1.0 inclusive")
        return v

class AlignmentResult(BaseModel):
    """
    A collection of claim alignments, tracking supported and unsupported claims.
    """
    alignments: List[ClaimAlignment] = Field(default_factory=list)
    unsupported_claim_ids: List[str] = Field(default_factory=list)
