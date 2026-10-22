from enum import Enum
from typing import List, Dict, Optional, Any, Literal
from pydantic import BaseModel, Field

class MainClass(str, Enum):
    C1 = "C1"  # Unchanged / Faithful
    C2 = "C2"  # Weakened
    C3 = "C3"  # Strengthened
    C4 = "C4"  # Unsupported addition
    C5 = "C5"  # Mixed strengthen + weaken

MAIN_CLASS_NAMES = {
    MainClass.C1: "UNCHANGED_FAITHFUL",
    MainClass.C2: "WEAKENED",
    MainClass.C3: "STRENGTHENED",
    MainClass.C4: "UNSUPPORTED_ADDITION",
    MainClass.C5: "MIXED",
}

class ShiftDirection(str, Enum):
    WEAKEN = "weaken"
    UNCHANGED = "unchanged"
    STRENGTHEN = "strengthen"

class ShiftSeverity(int, Enum):
    NONE = 0
    SLIGHT = 1
    MODERATE = 2
    SEVERE = 3

class AggressivenessLevel(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

class AttributeAnnotation(BaseModel):
    direction: ShiftDirection = ShiftDirection.UNCHANGED
    severity: int = Field(0, ge=0, le=3, description="0=none, 1=slight, 2=moderate, 3=severe")
    signed_shift: float = Field(0.0, description="Signed continuous shift magnitude in [-1.0, 1.0]")
    notes: Optional[str] = None

class ClaimAnnotation(BaseModel):
    claim_id: str
    main_class: MainClass
    attribute_shifts: Dict[str, AttributeAnnotation] = Field(default_factory=dict)
    reasons: List[str] = Field(default_factory=list)

class PairExample(BaseModel):
    example_id: str
    domain: str = "resumes_personal_statements"
    source_cluster_id: str = "cluster_0"
    source_text: str
    enhanced_text: str
    aggressiveness: Optional[AggressivenessLevel] = None
    generator_model: Optional[str] = None
    target_shift_types: List[str] = Field(default_factory=list)
    main_class: MainClass
    shift_vector: Dict[str, float] = Field(default_factory=dict)
    severity: float = 0.0
    annotations: List[ClaimAnnotation] = Field(default_factory=list)
    is_hard_case: bool = False
    is_minimal_pair: bool = False
    split: str = "train"  # train, val, test
    provenance: Literal["human", "llm", "system"] = "llm"
