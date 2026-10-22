import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from factsculpt.models import AtomicClaim, EvidenceProfile
from factsculpt.differencing.engine import AttributeDifferenceEngine
from factsculpt.features.generator import EvidenceDeviationFeatureGenerator
from factsculpt.classifier.rules import ResearchRuleBasedClassifier
from factsculpt.classifier.models import ClassificationCode, ClassificationResult

class RepairStepLog(BaseModel):
    iteration: int
    text_before: str
    text_after: str
    flagged_attributes: List[str]
    classification_code: str
    severity: float
    is_safe: bool

class RepairResult(BaseModel):
    original_source: str
    initial_enhanced: str
    repaired_text: str
    iterations_run: int
    stopped_reason: str
    initial_classification: str
    final_classification: str
    initial_severity: float
    final_severity: float
    steps: List[RepairStepLog] = Field(default_factory=list)

class AttributeTargetedRepairPipeline:
    """
    Iterative attribute-targeted repair system:
    GENERATE -> DETECT -> IDENTIFY FLAGGED ATTRIBUTES -> REWRITE ONLY FLAGGED ATTRIBUTES -> VERIFY -> REPEAT.
    
    Rather than regenerating the entire sentence and risking further hallucinations,
    it identifies exactly which attributes were inflated (e.g. certainty, role, scope, impact, quantity)
    and selectively edits them back into closed-world alignment.
    """

    def __init__(
        self,
        max_iterations: int = 3,
        severity_stop_threshold: float = 0.15
    ):
        self.max_iterations = max_iterations
        self.severity_stop_threshold = severity_stop_threshold
        self.differencer = AttributeDifferenceEngine()
        self.feature_generator = EvidenceDeviationFeatureGenerator()
        self.classifier = ResearchRuleBasedClassifier()

    def repair(self, source_text: str, enhanced_text: str) -> RepairResult:
        current_text = enhanced_text
        steps = []
        stopped_reason = "max_iterations_reached"

        initial_res = self._detect(source_text, enhanced_text)
        initial_code = initial_res.classification_code.value
        initial_sev = initial_res.severity

        # If already faithful or weakened, return immediately
        if initial_code in ("C1", "C2") or initial_sev <= self.severity_stop_threshold:
            return RepairResult(
                original_source=source_text,
                initial_enhanced=enhanced_text,
                repaired_text=enhanced_text,
                iterations_run=0,
                stopped_reason="already_safe",
                initial_classification=initial_code,
                final_classification=initial_code,
                initial_severity=initial_sev,
                final_severity=initial_sev,
                steps=[]
            )

        final_res = initial_res

        for i in range(1, self.max_iterations + 1):
            detection = self._detect(source_text, current_text)
            final_res = detection
            code = detection.classification_code.value
            sev = detection.severity

            # Identify flagged attributes with positive shift
            flagged = [
                attr for attr, shift in detection.shift_vector.items()
                if shift > 0.05
            ]

            if not flagged or code in ("C1", "C2") or sev <= self.severity_stop_threshold:
                stopped_reason = "safe_threshold_reached"
                break

            # Perform attribute-targeted rewrite
            repaired_text = self._rewrite_flagged_attributes(source_text, current_text, flagged, detection)

            step = RepairStepLog(
                iteration=i,
                text_before=current_text,
                text_after=repaired_text,
                flagged_attributes=flagged,
                classification_code=code,
                severity=sev,
                is_safe=False
            )
            steps.append(step)
            current_text = repaired_text

            # Verify
            new_detection = self._detect(source_text, current_text)
            final_res = new_detection
            if new_detection.classification_code.value in ("C1", "C2") or new_detection.severity <= self.severity_stop_threshold:
                step.is_safe = True
                stopped_reason = "verified_safe"
                break

        return RepairResult(
            original_source=source_text,
            initial_enhanced=enhanced_text,
            repaired_text=current_text,
            iterations_run=len(steps),
            stopped_reason=stopped_reason,
            initial_classification=initial_code,
            final_classification=final_res.classification_code.value,
            initial_severity=initial_sev,
            final_severity=final_res.severity,
            steps=steps
        )

    def _detect(self, source_text: str, generated_text: str) -> ClassificationResult:
        """Lightweight detection on text pair."""
        from factsculpt.extraction.llm import LLMEvidenceProfileExtractor
        from factsculpt.nli.models import EvidenceAnalysisResult, NLIResult, NLILabel
        from factsculpt.differencing.models import ProfileStatus

        profile_ext = LLMEvidenceProfileExtractor()
        src_c = AtomicClaim(claim_id="src", text=source_text, profile=profile_ext.extract_profile(AtomicClaim(claim_id="s", text=source_text)))
        gen_c = AtomicClaim(claim_id="gen", text=generated_text, profile=profile_ext.extract_profile(AtomicClaim(claim_id="g", text=generated_text)))

        diff = self.differencer.compare(src_c, gen_c)
        ent_score = round(max(0.0, min(1.0, 1.0 - diff.severity)), 4)
        neu_score = round(max(0.0, min(1.0, diff.severity)), 4)
        analysis = EvidenceAnalysisResult(
            source_claim_id="src",
            generated_claim_id="gen",
            nli_result=NLIResult(
                source_claim_id="src",
                generated_claim_id="gen",
                label=NLILabel.ENTAILMENT if diff.severity <= self.severity_stop_threshold else NLILabel.NEUTRAL,
                entailment_score=ent_score,
                neutral_score=neu_score,
                contradiction_score=0.0,
                model_name="repair_nli"
            ),
            attribute_difference=diff
        )
        feats = self.feature_generator.generate(analysis, semantic_similarity=ent_score)
        return self.classifier.classify(feats)

    def _rewrite_flagged_attributes(
        self,
        source_text: str,
        current_text: str,
        flagged: List[str],
        detection: ClassificationResult
    ) -> str:
        """
        Substitutes only the flagged inflated attributes back to the source evidence levels.
        """
        text = current_text

        # 1. Role inflation
        if "role" in flagged:
            # Demote inflated verbs
            text = re.sub(r"\b(spearheaded|architected|founded and led|managed|directed|led the engineering of|led the development of)\b", "assisted with developing", text, flags=re.IGNORECASE)
            text = re.sub(r"\b(led)\b", "assisted with", text, flags=re.IGNORECASE)

        # 2. Scope expansion
        if "scope" in flagged:
            # Contract global/worldwide -> regional/local
            text = re.sub(r"\b(globally|worldwide|enterprise-wide|across all international facilities)\b", "regionally", text, flags=re.IGNORECASE)
            text = re.sub(r"\b(global|worldwide)\b", "regional", text, flags=re.IGNORECASE)

        # 3. Certainty inflation
        if "certainty" in flagged:
            # Soften assertions back to possibility/hedging
            text = re.sub(r"\b(definitely|guaranteed|proved|confirmed|will)\b", "potentially", text, flags=re.IGNORECASE)
            text = re.sub(r"\b(guaranteed decreased|definitely indicated)\b", "possibly indicated", text, flags=re.IGNORECASE)

        # 4. Qualifier inflation
        if "qualifier" in flagged:
            # Remove promotional superlatives
            text = re.sub(r"\b(cutting-edge|state-of-the-art|sophisticated|industry-leading|mission-critical|advanced)\s*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s+", " ", text).strip()

        # 5. Impact inflation
        if "impact" in flagged:
            text = re.sub(r"\b(massive improvement|transformational quality gains|dramatic latency reduction|high impact)\b", "improved efficiency", text, flags=re.IGNORECASE)

        # 6. Quantity inflation
        if "quantity" in flagged:
            # Look for inflated numbers or bounds: e.g. "over X" -> "approximately X"
            text = re.sub(r"\bover\s+(\d+)\b", r"approximately \1", text, flags=re.IGNORECASE)
            # Revert inflated quantities if source text contains distinct numeric bounds
            src_nums = re.findall(r"\b\d+\b", source_text)
            text_nums = re.findall(r"\b\d+\b", text)
            if src_nums and text_nums and src_nums != text_nums:
                if len(src_nums) == 1 and len(text_nums) == 1:
                    text = re.sub(r"\b" + text_nums[0] + r"\b", src_nums[0], text)

        return text
