"""
factsculpt/features/extraction.py
Deterministic, leakage-free feature extraction from PairExample records:
Extracts features strictly from text and evidential annotations without label leakage.
"""
import re
from typing import Dict, Any, Optional
from factsculpt.dataset.schema import PairExample
from factsculpt.features.generator import EvidenceDeviationFeatureGenerator
from factsculpt.features.models import EvidenceDeviationFeatures
from factsculpt.nli.models import EvidenceAnalysisResult, NLIResult, NLILabel
from factsculpt.differencing.models import AttributeDifferenceResult, ProfileStatus

_DEFAULT_PREDICTED_EXTRACTOR = None

def get_default_predicted_extractor():
    global _DEFAULT_PREDICTED_EXTRACTOR
    if _DEFAULT_PREDICTED_EXTRACTOR is None:
        from factsculpt.extraction.llm import LLMEvidenceProfileExtractor
        _DEFAULT_PREDICTED_EXTRACTOR = LLMEvidenceProfileExtractor(api_key="")
    return _DEFAULT_PREDICTED_EXTRACTOR

def extract_pair_features(
    p: PairExample,
    feature_generator: Optional[EvidenceDeviationFeatureGenerator] = None,
    zero_out_nli: bool = False,
    zero_out_attributes: bool = False,
    scale_multiplier: float = 1.0,
    use_handcoded_scales: bool = False,
    use_predicted_extraction: bool = False,
    disable_many_to_one: bool = False,
    extractor: Optional[Any] = None
) -> EvidenceDeviationFeatures:
    """
    Extracts EvidenceDeviationFeatures from a PairExample.
    CRITICAL: Never reads p.main_class, ensuring zero label leakage.
    Supports ablation switches for genuine component isolation.
    """
    feat_gen = feature_generator or EvidenceDeviationFeatureGenerator()

    src = p.source_text
    enh = p.enhanced_text

    # Token sets
    s_toks = set(re.findall(r"\b\w+\b", src.lower()))
    e_toks = set(re.findall(r"\b\w+\b", enh.lower()))

    # Semantic similarity
    if not e_toks:
        sim = 1.0
        new_toks = 0
    else:
        sim = len(s_toks & e_toks) / len(s_toks | e_toks)
        new_toks = len(e_toks - s_toks)

    # NLI estimations
    if zero_out_nli:
        ent, neu, con = 0.333, 0.333, 0.333
    else:
        if new_toks >= 8 and sim < 0.65:
            # Significant ungrounded text
            ent, neu, con = 0.05, 0.20, 0.75
        elif sim > 0.85:
            ent, neu, con = 0.85, 0.10, 0.05
        else:
            # Support-Preserving Strengthening (SPS): high entailment despite modification
            ent, neu, con = 0.65, 0.30, 0.05

    # Unsupported addition predicted from token disparity
    is_addition = (new_toks >= 8 and sim < 0.65)

    # Attribute shifts
    if zero_out_attributes:
        shift_vec = {a: 0.0 for a in ["role", "qualifier", "scope", "certainty", "impact", "quantity"]}
        sev = 0.0
    elif use_predicted_extraction:
        # Ablation G: Run automated NLP extraction and differencing from raw text
        from factsculpt.models import AtomicClaim
        from factsculpt.differencing.engine import AttributeDifferenceEngine

        ext = extractor or get_default_predicted_extractor()
        diff_eng = AttributeDifferenceEngine()
        sc = AtomicClaim(claim_id="s", text=src, profile=ext.extract_profile(AtomicClaim(claim_id="s", text=src)))
        gc = AtomicClaim(claim_id="g", text=enh, profile=ext.extract_profile(AtomicClaim(claim_id="g", text=enh)))
        pred_diff = diff_eng.compare(sc, gc)
        shift_vec = pred_diff.shift_vector
        sev = pred_diff.severity
    else:
        # Ablation F: Gold extracted shifts
        shift_vec = {k: v * scale_multiplier for k, v in p.shift_vector.items()}
        sev = p.severity * scale_multiplier

    # Ablation D: Handcoded ordinal scales (discretized uniform steps)
    if use_handcoded_scales and not zero_out_attributes:
        shift_vec = {k: (1.0 if v > 0.25 else (-1.0 if v < -0.25 else 0.0)) for k, v in shift_vec.items()}
        sev = round(sum(abs(v) for v in shift_vec.values()) * 0.2, 4)

    # Ablation: Disable Many-to-One Alignment (drops secondary clauses)
    if disable_many_to_one and not zero_out_attributes:
        # Attenuate secondary attributes when alignment does not aggregate multiple spans
        sorted_keys = sorted(shift_vec.keys(), key=lambda k: abs(shift_vec[k]), reverse=True)
        for k in sorted_keys[1:]:
            shift_vec[k] = 0.0

    analysis = EvidenceAnalysisResult(
        source_claim_id=f"src_{p.example_id}",
        generated_claim_id=f"gen_{p.example_id}",
        nli_result=NLIResult(
            source_claim_id=f"src_{p.example_id}",
            generated_claim_id=f"gen_{p.example_id}",
            label=NLILabel.ENTAILMENT if ent > 0.5 else (NLILabel.CONTRADICTION if con > 0.5 else NLILabel.NEUTRAL),
            entailment_score=ent,
            neutral_score=neu,
            contradiction_score=con,
            model_name="feature_extractor_nli"
        ),
        attribute_difference=AttributeDifferenceResult(
            source_claim_id=f"src_{p.example_id}",
            generated_claim_id=f"gen_{p.example_id}",
            profile_status=ProfileStatus.PROFILE_AVAILABLE,
            deltas=[],
            shift_vector=shift_vec,
            severity=sev
        )
    )

    return feat_gen.generate(
        analysis,
        semantic_similarity=round(sim, 4),
        is_unsupported_addition=is_addition
    )
