import math
from typing import List

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """
    Calculates the cosine similarity between two numeric vectors.

    If either vector has a magnitude of 0 (a zero vector), returns 0.0.
    If the lengths of v1 and v2 are different, raises a ValueError.

    Args:
        v1: First vector as a list of floats.
        v2: Second vector as a list of floats.

    Returns:
        Cosine similarity score clamped between -1.0 and 1.0.
    """
    if len(v1) != len(v2):
        raise ValueError(f"Vector dimensions must match (got lengths {len(v1)} and {len(v2)}).")

    dot_product = sum(a * b for a, b in zip(v1, v2))
    sum_sq1 = sum(a * a for a in v1)
    sum_sq2 = sum(b * b for b in v2)

    magnitude1 = math.sqrt(sum_sq1)
    magnitude2 = math.sqrt(sum_sq2)

    if magnitude1 == 0.0 or magnitude2 == 0.0:
        return 0.0

    score = dot_product / (magnitude1 * magnitude2)

    # Clamp the result to [-1.0, 1.0] to avoid minor floating-point precision errors
    return max(-1.0, min(1.0, score))
