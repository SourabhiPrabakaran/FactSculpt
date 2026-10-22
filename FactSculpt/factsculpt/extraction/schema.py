"""
factsculpt/extraction/schema.py
Strict JSON Schema and definitions for closed-world Evidence Profile extraction.
Covers the 6 core evidential attributes:
- role_agency
- qualifier
- scope
- certainty
- impact
- quantity (quantitative_info)
Plus per-attribute and overall confidence scores.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

STRICT_PROFILE_EXTRACTION_JSON_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "StrictEvidenceProfile",
    "description": "Closed-world extraction of semantic evidence attributes from an atomic claim.",
    "type": "object",
    "properties": {
        "role_agency": {
            "type": "object",
            "description": "Leadership role or individual agency level (e.g. assisted, led, managed, contributed, null).",
            "properties": {
                "value": {"type": ["string", "null"]},
                "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}
            },
            "required": ["value", "confidence"]
        },
        "qualifier": {
            "type": "object",
            "description": "Adjective or descriptor of complexity, novelty, or scale (e.g. advanced, cutting-edge, state-of-the-art, null).",
            "properties": {
                "value": {"type": ["string", "null"]},
                "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}
            },
            "required": ["value", "confidence"]
        },
        "scope": {
            "type": "object",
            "description": "Organizational or geographic operational reach (e.g. global, regional, local, enterprise-wide, null).",
            "properties": {
                "value": {"type": ["string", "null"]},
                "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}
            },
            "required": ["value", "confidence"]
        },
        "certainty": {
            "type": "object",
            "description": "Epistemic modality or certainty level (e.g. high, low, tentative, certain, null).",
            "properties": {
                "value": {"type": ["string", "null"]},
                "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}
            },
            "required": ["value", "confidence"]
        },
        "impact": {
            "type": "object",
            "description": "Technical or business outcome/impact (e.g. high impact, improved efficiency, minimal impact, null).",
            "properties": {
                "value": {"type": ["string", "null"]},
                "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}
            },
            "required": ["value", "confidence"]
        },
        "quantity": {
            "type": "object",
            "description": "Numeric metrics, percentages, multipliers, durations (e.g. 5, 10x, 40%, 3 years, null).",
            "properties": {
                "value": {"type": ["string", "null"]},
                "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}
            },
            "required": ["value", "confidence"]
        },
        "overall_confidence": {
            "type": "number",
            "description": "Aggregated confidence score across all extracted attributes (0.0 to 1.0).",
            "minimum": 0.0,
            "maximum": 1.0
        }
    },
    "required": [
        "role_agency",
        "qualifier",
        "scope",
        "certainty",
        "impact",
        "quantity",
        "overall_confidence"
    ],
    "additionalProperties": False
}


class AttributeValueWithConfidence(BaseModel):
    value: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class StrictEvidenceProfilePayload(BaseModel):
    role_agency: AttributeValueWithConfidence
    qualifier: AttributeValueWithConfidence
    scope: AttributeValueWithConfidence
    certainty: AttributeValueWithConfidence
    impact: AttributeValueWithConfidence
    quantity: AttributeValueWithConfidence
    overall_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
