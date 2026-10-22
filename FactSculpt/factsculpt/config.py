import os
from typing import Optional
from pydantic import BaseModel, Field

class FactSculptConfig(BaseModel):
    """
    Configuration for the FACTSculpt prototype.
    Ensures that model names and parameters are configurable and not hard-coded.
    """
    claim_extractor_model: str = Field(
        default="gemini-2.5-flash",
        description="Model identifier for the atomic claim extraction task"
    )
    profile_extractor_model: str = Field(
        default="gemini-2.5-flash",
        description="Model identifier for the evidence profile extraction task"
    )
    api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("FACTSCULPT_API_KEY"),
        description="API key for external LLM calls (e.g., Gemini API)"
    )
    temperature: float = Field(
        default=0.0,
        description="Temperature for generation"
    )
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Model identifier for the sentence embedding generator"
    )
    similarity_threshold: float = Field(
        default=0.5,
        description="Similarity threshold to define when claims are semantically aligned"
    )
    nli_model: str = Field(
        default="cross-encoder/nli-MiniLM2-L6-H768",
        description="Model identifier for the Natural Language Inference (NLI) classifier"
    )
