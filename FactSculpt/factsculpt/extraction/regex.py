"""
factsculpt/extraction/regex.py
Deterministic Regex-Based Evidence Profile Extractor.
Serves as the explicit offline fallback and comparative baseline for LLMEvidenceProfileExtractor.
"""

import re
import logging
from typing import Dict, Optional, Any
from factsculpt.models import AtomicClaim, EvidenceProfile
from factsculpt.extraction.interfaces import EvidenceProfileExtractor

logger = logging.getLogger(__name__)


class RegexEvidenceProfileExtractor(EvidenceProfileExtractor):
    """
    Heuristic, pattern-based EvidenceProfile extractor.
    Extracts the six core attributes (role_agency, qualifier, scope, certainty, impact, quantity)
    plus entity, activity, object, and domain via curated regular expressions.
    """

    def __init__(self):
        pass

    def extract_profile(self, claim: AtomicClaim) -> EvidenceProfile:
        return self.extract_from_text(claim.text)

    def extract_from_text(self, text: str) -> EvidenceProfile:
        t = text.lower()
        kwargs: Dict[str, Optional[str]] = {}
        confidences: Dict[str, float] = {
            "role_agency": 1.0,
            "activity_action": 1.0,
            "object": 1.0,
            "domain": 1.0,
            "certainty": 1.0,
            "qualifier": 1.0,
            "scope": 1.0,
            "impact": 1.0,
            "quantitative_info": 1.0,
            "subject_entity": 1.0
        }

        # 0. Subject entity
        subj_match = re.search(r"\b(i|we|my team|our team|the author|the candidate)\b", t)
        if subj_match:
            kwargs["subject_entity"] = subj_match.group(1)
            confidences["subject_entity"] = 0.95

        # 1. Role agency
        if re.search(r"\b(led|lead|directed|spearheaded|founded|managed|architected|owned)\b", t):
            kwargs["role_agency"] = "led"
            confidences["role_agency"] = 0.95
        elif re.search(r"\b(assisted|helped|supported|contributed|participated|co-developed|shadowed)\b", t):
            kwargs["role_agency"] = "assisted"
            confidences["role_agency"] = 0.95

        # 2. Activity / action
        action_match = re.search(r"\b(developing|developed|development|develop|designing|designed|design|deployed|deploy|deployment|created|creation|built|architected|implementation|implemented|analyzed|analyzing|engineered|tested)\b", t)
        if action_match:
            kwargs["activity_action"] = action_match.group(1)
            confidences["activity_action"] = 0.90

        # 3. Qualifier
        qual_match = re.search(r"\b(advanced|cutting-edge|sophisticated|highly efficient|state-of-the-art|modern|complex|scalable|industry-leading|mission-critical|robust)\b", t)
        if qual_match:
            kwargs["qualifier"] = qual_match.group(1)
            confidences["qualifier"] = 0.92

        # 4. Scope
        scope_match = re.search(r"\b(global|globally|worldwide|national|nationwide|regional|regionally|locally|local|enterprise-wide|company-wide)\b", t)
        if scope_match:
            s_val = scope_match.group(1)
            if "global" in s_val or "worldwide" in s_val:
                kwargs["scope"] = "global"
            elif "national" in s_val:
                kwargs["scope"] = "national"
            elif "regional" in s_val:
                kwargs["scope"] = "regional"
            elif "local" in s_val:
                kwargs["scope"] = "local"
            elif "enterprise" in s_val or "company" in s_val:
                kwargs["scope"] = "enterprise-wide"
            confidences["scope"] = 0.94

        # 5. Certainty
        if re.search(r"\b(definitely|certainly|highly certain|guaranteed|always|proved|proven|confirmed|will)\b", t):
            kwargs["certainty"] = "high"
            confidences["certainty"] = 0.90
        elif re.search(r"\b(possibly|might|maybe|perhaps|low certainty|potentially|could|tentative|tentatively|preliminary|exploratory|may)\b", t):
            kwargs["certainty"] = "low"
            confidences["certainty"] = 0.90

        # 6. Impact
        if re.search(r"\b(high impact|improved efficiency|massive improvement|massive|huge|tremendous|significant|transformational|optimized performance)\b", t):
            kwargs["impact"] = "high impact"
            confidences["impact"] = 0.90
        elif re.search(r"\b(low impact|minimal impact|negligible|minor impact|slight|modest|marginal)\b", t):
            kwargs["impact"] = "low impact"
            confidences["impact"] = 0.90

        # 7. Quantitative info
        quant_match = re.search(r"\b(over\s+\d+|more\s+than\s+\d+|approximately\s+\d+|about\s+\d+|\d+\s*(?:years?|months?|days?|x|users?|datasets?|ms|k|m|b|\+))\b|(\d+(?:\.\d+)?%)", t)
        if quant_match:
            kwargs["quantitative_info"] = quant_match.group(1) or quant_match.group(2)
            confidences["quantitative_info"] = 0.95

        # 8. Domain
        domain_match = re.search(r"\b(pharmacy|banking|finance|fintech|healthcare|ev charger(?: monitoring)?|e-commerce|aerospace|cloud|distributed systems)\b", t)
        if domain_match:
            kwargs["domain"] = domain_match.group(1)
            confidences["domain"] = 0.90

        # 9. Object
        obj_match = re.search(r"\b(system|application|app|platform|pipeline|database|infrastructure|tool|model|prototype|service|api)\b", t)
        if obj_match:
            kwargs["object"] = obj_match.group(1)
            confidences["object"] = 0.90

        overall = sum(confidences.values()) / len(confidences)
        return EvidenceProfile(
            **kwargs,
            attribute_confidences=confidences,
            overall_confidence=round(overall, 4)
        )
