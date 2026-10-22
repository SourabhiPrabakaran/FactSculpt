from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class ChangeType(str, Enum):
    UNCHANGED = "UNCHANGED"
    ADDED = "ADDED"
    REMOVED = "REMOVED"
    MODIFIED = "MODIFIED"

class Direction(str, Enum):
    UNCHANGED = "UNCHANGED"
    STRENGTHENED = "STRENGTHENED"
    WEAKENED = "WEAKENED"
    EXPANDED = "EXPANDED"
    REDUCED = "REDUCED"
    CHANGED = "CHANGED"

class ProfileStatus(str, Enum):
    PROFILE_AVAILABLE = "PROFILE_AVAILABLE"
    PROFILE_MISSING_SOURCE = "PROFILE_MISSING_SOURCE"
    PROFILE_MISSING_GENERATED = "PROFILE_MISSING_GENERATED"
    BOTH_PROFILES_MISSING = "BOTH_PROFILES_MISSING"

VALID_ATTRIBUTES = {
    "role_agency",
    "activity_action",
    "object",
    "domain",
    "certainty",
    "qualifier",
    "scope",
    "impact",
    "quantitative_info"
}

class AttributeDelta(BaseModel):
    """
    Structured delta of a single EvidenceProfile attribute.
    """
    attribute_name: str
    source_value: Optional[str] = None
    generated_value: Optional[str] = None
    change_type: ChangeType
    direction: Direction

    @field_validator("attribute_name")
    @classmethod
    def check_valid_attribute_name(cls, v: str) -> str:
        if v not in VALID_ATTRIBUTES:
            raise ValueError(
                f"Invalid attribute_name: '{v}'. Must be one of the EvidenceProfile fields: {sorted(VALID_ATTRIBUTES)}"
            )
        return v

class AttributeDifferenceResult(BaseModel):
    """
    Comparison result containing all attribute deltas between aligned claims.
    """
    source_claim_id: Optional[str] = None
    generated_claim_id: str
    profile_status: ProfileStatus
    deltas: List[AttributeDelta] = Field(default_factory=list)
    shift_vector: dict = Field(default_factory=dict, description="Signed shift vector across 6 core attributes")
    severity: float = Field(0.0, description="Overall calibrated severity score")

    @field_validator("generated_claim_id")
    @classmethod
    def check_non_empty_generated_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("generated_claim_id cannot be empty or whitespace-only")
        return v.strip()

