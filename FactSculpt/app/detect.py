import os
import sys
import json
import argparse
from typing import Dict, Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from factsculpt.models import AtomicClaim
from factsculpt.extraction.llm import LLMEvidenceProfileExtractor
from factsculpt.differencing.engine import AttributeDifferenceEngine
from factsculpt.features.generator import EvidenceDeviationFeatureGenerator
from factsculpt.classifier.rules import ResearchRuleBasedClassifier
from factsculpt.nli.models import EvidenceAnalysisResult, NLIResult, NLILabel
from factsculpt.experiments.baselines import NLIOnlyBaseline
from factsculpt.nli.models_hf import HuggingFaceNLIClassifier

def read_text_or_file(input_val: str) -> str:
    if os.path.isfile(input_val):
        with open(input_val, "r", encoding="utf-8") as f:
            return f.read().strip()
    return input_val.strip()

def detect(source_text: str, enhanced_text: str, use_hf_nli: bool = False) -> Dict[str, Any]:
    """
    Demo/reference CLI detection function for evidence exaggeration.
    Extracts evidence profiles, computes multi-dimensional attribute differences,
    evaluates dynamic textual NLI scores, and classifies using research rule heuristics.
    """
    profile_extractor = LLMEvidenceProfileExtractor()
    differencer = AttributeDifferenceEngine()
    feature_gen = EvidenceDeviationFeatureGenerator()
    classifier = ResearchRuleBasedClassifier()

    src_c = AtomicClaim(
        claim_id="src_1",
        text=source_text,
        profile=profile_extractor.extract_profile(AtomicClaim(claim_id="s", text=source_text))
    )
    gen_c = AtomicClaim(
        claim_id="gen_1",
        text=enhanced_text,
        profile=profile_extractor.extract_profile(AtomicClaim(claim_id="g", text=enhanced_text))
    )

    diff = differencer.compare(src_c, gen_c)
    
    # Dynamic NLI score calculation on source and enhanced texts
    nli_model_name = "nli_text_baseline"
    if use_hf_nli:
        try:
            hf_clf = HuggingFaceNLIClassifier()
            nli_res = hf_clf.predict(source_text, enhanced_text)
            label = nli_res.label
            ent_score = nli_res.entailment_score
            neu_score = nli_res.neutral_score
            con_score = nli_res.contradiction_score
            nli_model_name = hf_clf.model_name
        except Exception:
            baseline = NLIOnlyBaseline()
            ent_score, neu_score, con_score = baseline._estimate_nli_scores(source_text, enhanced_text)
            label = NLILabel.ENTAILMENT if ent_score >= 0.65 else (NLILabel.CONTRADICTION if con_score >= 0.45 else NLILabel.NEUTRAL)
    else:
        baseline = NLIOnlyBaseline()
        ent_score, neu_score, con_score = baseline._estimate_nli_scores(source_text, enhanced_text)
        label = NLILabel.ENTAILMENT if ent_score >= 0.65 else (NLILabel.CONTRADICTION if con_score >= 0.45 else NLILabel.NEUTRAL)

    analysis = EvidenceAnalysisResult(
        source_claim_id="src_1",
        generated_claim_id="gen_1",
        nli_result=NLIResult(
            source_claim_id="src_1",
            generated_claim_id="gen_1",
            label=label,
            entailment_score=ent_score,
            neutral_score=neu_score,
            contradiction_score=con_score,
            model_name=nli_model_name
        ),
        attribute_difference=diff
    )

    feats = feature_gen.generate(analysis, semantic_similarity=0.85)
    res = classifier.classify(feats)

    output = {
        "is_demo_cli": True,
        "classification": res.classification_code.value,
        "classification_name": res.classification_name,
        "severity": res.severity,
        "shift_vector": res.shift_vector,
        "confidence": res.confidence,
        "abstain": res.abstain,
        "reasons": res.reasons,
        "nli_support": {
            "label": label.value,
            "entailment": round(ent_score, 4),
            "neutral": round(neu_score, 4),
            "contradiction": round(con_score, 4)
        }
    }
    return output

def main():
    parser = argparse.ArgumentParser(
        description="FactSculpt [DEMO]: Closed-World Exaggeration Detection Reference CLI"
    )
    parser.add_argument("--source", type=str, required=True, help="Path to source text file or raw source text")
    parser.add_argument("--enhanced", type=str, required=True, help="Path to enhanced text file or raw enhanced text")
    parser.add_argument("--use-hf-nli", action="store_true", help="Attempt loading heavy pretrained HuggingFace NLI cross-encoder")
    args = parser.parse_args()

    src_text = read_text_or_file(args.source)
    gen_text = read_text_or_file(args.enhanced)

    result = detect(src_text, gen_text, use_hf_nli=args.use_hf_nli)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
