from typing import Optional, List, Dict
from pydantic import BaseModel, Field, model_validator, field_validator

class EvidenceProfile(BaseModel):
    """
    Structured evidence profile containing fields representing the semantics
    and evidence profile of an atomic claim.
    """
    role_agency: Optional[str] = Field(None, description="The role or agency of the subject (e.g. assisted, led)")
    activity_action: Optional[str] = Field(None, description="The activity or action performed")
    object: Optional[str] = Field(None, description="The object or entity acted upon")
    domain: Optional[str] = Field(None, description="The domain or field of study/work")
    certainty: Optional[str] = Field(None, description="The certainty level or modality")
    qualifier: Optional[str] = Field(None, description="Qualifying adjectives or adverbs (e.g. advanced)")
    scope: Optional[str] = Field(None, description="The scope or coverage area")
    impact: Optional[str] = Field(None, description="The impact or result of the action")
    quantitative_info: Optional[str] = Field(None, description="Quantitative values, metrics, or numbers")
    subject_entity: Optional[str] = Field(None, description="The subject or entity performing the action")
    attribute_confidences: Dict[str, float] = Field(default_factory=dict, description="Extraction confidence per attribute (0.0 to 1.0)")
    overall_confidence: float = Field(1.0, description="Overall profile extraction confidence")

    @property
    def role(self) -> Optional[str]:
        return self.role_agency

    @role.setter
    def role(self, val: Optional[str]):
        self.role_agency = val

    @property
    def quantity(self) -> Optional[str]:
        return self.quantitative_info

    @quantity.setter
    def quantity(self, val: Optional[str]):
        self.quantitative_info = val

    @model_validator(mode="after")
    def clean_empty_strings(self) -> "EvidenceProfile":
        # Convert any empty or whitespace-only string fields to None
        for field_name in ["role_agency", "activity_action", "object", "domain", "certainty", "qualifier", "scope", "impact", "quantitative_info", "subject_entity"]:
            val = getattr(self, field_name, None)
            if isinstance(val, str) and not val.strip():
                setattr(self, field_name, None)
        return self

class AtomicClaim(BaseModel):
    """
    An individual atomic claim extracted from a text block, retaining provenance.
    """
    claim_id: str
    text: str
    source_text_id: Optional[str] = None
    span_start: Optional[int] = None
    span_end: Optional[int] = None
    evidence_span: Optional[str] = None
    confidence: float = Field(1.0, description="Confidence in atomic claim extraction")
    profile: Optional[EvidenceProfile] = None

    @field_validator("claim_id", "text")
    @classmethod
    def check_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace-only")
        return v.strip()

    @model_validator(mode="after")
    def validate_spans(self) -> "AtomicClaim":
        if self.span_start is not None and self.span_start < 0:
            raise ValueError("span_start cannot be negative")
        if self.span_end is not None and self.span_end < 0:
            raise ValueError("span_end cannot be negative")
        if self.span_start is not None and self.span_end is not None:
            if self.span_start > self.span_end:
                raise ValueError("span_start must be less than or equal to span_end")
        return self

class ExtractionResult(BaseModel):
    """
    Container for all atomic claims extracted from a source text.
    """
    source_text_id: str
    source_text: str
    claims: List[AtomicClaim] = Field(default_factory=list)

    @field_validator("source_text_id", "source_text")
    @classmethod
    def check_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace-only")
        return v.strip()

