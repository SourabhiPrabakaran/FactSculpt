import re
from typing import List
from factsculpt.models import AtomicClaim, EvidenceProfile
from factsculpt.extraction.interfaces import AtomicClaimExtractor, EvidenceProfileExtractor

class MockAtomicClaimExtractor(AtomicClaimExtractor):
    """
    Mock atomic claim extractor using simple punctuation-based sentence splitting.
    Tracks exact span positions and generates unique claim IDs.
    """

    def extract_claims(self, text: str) -> List[AtomicClaim]:
        if not text or not text.strip():
            return []

        claims = []
        # Match sentences ending with ., !, or ? (or end of string)
        pattern = re.compile(r"[^.!?]+(?:[.!?]+|$)")
        for match in pattern.finditer(text):
            sentence = match.group(0)
            span_start = match.start()
            span_end = match.end()

            # Trim whitespace from the match to get exact spans
            left_strip_len = len(sentence) - len(sentence.lstrip())
            right_strip_len = len(sentence) - len(sentence.rstrip())

            clean_sentence = sentence.strip()
            if not clean_sentence:
                continue

            clean_start = span_start + left_strip_len
            clean_end = span_end - right_strip_len

            claim_id = f"claim_{len(claims)}"

            claims.append(
                AtomicClaim(
                    claim_id=claim_id,
                    text=clean_sentence,
                    span_start=clean_start,
                    span_end=clean_end,
                )
            )
        return claims

class MockEvidenceProfileExtractor(EvidenceProfileExtractor):
    """
    Mock evidence profile extractor recognizing simple deterministic keywords.
    NOTE: This is only for testing interfaces and is not the final NLP algorithm.
    """

    def extract_profile(self, claim: AtomicClaim) -> EvidenceProfile:
        text_lower = claim.text.lower()
        profile_kwargs = {}

        # Deterministic role_agency mapping
        if "assisted" in text_lower:
            profile_kwargs["role_agency"] = "assisted"
        elif "led" in text_lower:
            profile_kwargs["role_agency"] = "led"

        # Deterministic activity_action mapping
        if "developing" in text_lower:
            profile_kwargs["activity_action"] = "developing"
        elif "developed" in text_lower:
            profile_kwargs["activity_action"] = "developed"
        elif "develop" in text_lower:
            profile_kwargs["activity_action"] = "develop"

        # Deterministic qualifier mapping
        if "advanced" in text_lower:
            profile_kwargs["qualifier"] = "advanced"

        # Deterministic object mapping
        if "system" in text_lower:
            profile_kwargs["object"] = "system"

        # Basic mappings for remaining fields if mock words appear in the text
        if "ev charger" in text_lower:
            profile_kwargs["domain"] = "EV charger monitoring"
        if "highly certain" in text_lower or "definitely" in text_lower:
            profile_kwargs["certainty"] = "high"
        if "global" in text_lower:
            profile_kwargs["scope"] = "global"
        if "improved efficiency" in text_lower:
            profile_kwargs["impact"] = "improved efficiency"
        if "100%" in text_lower or "5" in text_lower:
            profile_kwargs["quantitative_info"] = "5"

        return EvidenceProfile(**profile_kwargs)
