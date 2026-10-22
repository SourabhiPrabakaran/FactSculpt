# Alignment package initialization
from factsculpt.alignment.interfaces import EmbeddingGenerator, ClaimAligner
from factsculpt.alignment.models import ClaimAlignment, AlignmentResult
from factsculpt.alignment.cosine import cosine_similarity
from factsculpt.alignment.embeddings import SentenceTransformerEmbeddingGenerator, MockEmbeddingGenerator
from factsculpt.alignment.aligner import EmbeddingClaimAligner

__all__ = [
    "EmbeddingGenerator",
    "ClaimAligner",
    "ClaimAlignment",
    "AlignmentResult",
    "cosine_similarity",
    "SentenceTransformerEmbeddingGenerator",
    "MockEmbeddingGenerator",
    "EmbeddingClaimAligner",
]
