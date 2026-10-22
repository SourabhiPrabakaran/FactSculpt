import os
import re
import json
import logging
from typing import List, Optional, Dict, Any
from factsculpt.config import FactSculptConfig
from factsculpt.models import AtomicClaim, EvidenceProfile
from factsculpt.extraction.interfaces import AtomicClaimExtractor, EvidenceProfileExtractor
from factsculpt.extraction.schema import STRICT_PROFILE_EXTRACTION_JSON_SCHEMA
from factsculpt.extraction.cache import ProfileResponseCache
from factsculpt.extraction.regex import RegexEvidenceProfileExtractor

logger = logging.getLogger(__name__)

CLAIM_EXTRACTION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim_id": {"type": "string"},
                    "text": {"type": "string"},
                    "evidence_span": {"type": "string"},
                    "span_start": {"type": "integer"},
                    "span_end": {"type": "integer"},
                    "confidence": {"type": "number"}
                },
                "required": ["text", "confidence"]
            }
        }
    },
    "required": ["claims"]
}

PROFILE_EXTRACTION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "subject_entity": {"type": "object", "properties": {"value": {"type": ["string", "null"]}, "confidence": {"type": "number"}}},
        "role_agency": {"type": "object", "properties": {"value": {"type": ["string", "null"]}, "confidence": {"type": "number"}}},
        "activity_action": {"type": "object", "properties": {"value": {"type": ["string", "null"]}, "confidence": {"type": "number"}}},
        "object": {"type": "object", "properties": {"value": {"type": ["string", "null"]}, "confidence": {"type": "number"}}},
        "domain": {"type": "object", "properties": {"value": {"type": ["string", "null"]}, "confidence": {"type": "number"}}},
        "certainty": {"type": "object", "properties": {"value": {"type": ["string", "null"]}, "confidence": {"type": "number"}}},
        "qualifier": {"type": "object", "properties": {"value": {"type": ["string", "null"]}, "confidence": {"type": "number"}}},
        "scope": {"type": "object", "properties": {"value": {"type": ["string", "null"]}, "confidence": {"type": "number"}}},
        "impact": {"type": "object", "properties": {"value": {"type": ["string", "null"]}, "confidence": {"type": "number"}}},
        "quantitative_info": {"type": "object", "properties": {"value": {"type": ["string", "null"]}, "confidence": {"type": "number"}}},
        "overall_confidence": {"type": "number"}
    }
}

EXTRACTION_SYSTEM_PROMPT = """You are a precise NLP linguistic extraction system.
Extract atomic factual claims from the provided text under a closed-world assumption.
An atomic claim is an indivisible factual statement with a single subject, action/event, or attribution.
Do not infer unstated facts or exaggerate.

FEW-SHOT EXAMPLE:
Input: "I assisted with developing an EV charger monitoring system. We deployed it regionally."
Output:
{
  "claims": [
    {
      "claim_id": "C1",
      "text": "I assisted with developing an EV charger monitoring system.",
      "evidence_span": "I assisted with developing an EV charger monitoring system.",
      "span_start": 0,
      "span_end": 58,
      "confidence": 0.98
    },
    {
      "claim_id": "C2",
      "text": "We deployed it regionally.",
      "evidence_span": "We deployed it regionally.",
      "span_start": 59,
      "span_end": 85,
      "confidence": 0.95
    }
  ]
}

Return ONLY valid JSON matching this schema:
{
  "claims": [
    {
      "claim_id": "C1",
      "text": "...",
      "evidence_span": "...",
      "span_start": 0,
      "span_end": 45,
      "confidence": 0.95
    }
  ]
}
"""

PROFILE_SYSTEM_PROMPT = """You are a semantic evidence profiler.
Given an atomic claim, extract its semantic evidence attributes according to the closed-world taxonomy.
Provide an attribute value and extraction confidence (0.0 to 1.0) for every attribute.
If an attribute is not explicitly mentioned or implied by the closed-world text, set value to null and confidence to 1.0.

Attributes:
1. subject_entity: The person, team, or entity performing or receiving the action (e.g. "I", "our team", "the model").
2. role_agency: The role, leadership level, or agency (e.g. "assisted", "led", "contributed", "managed", "directed", "conducted").
3. activity_action: The primary action or technical verb (e.g. "developing", "designed", "deployed", "implemented", "analyzed").
4. object: Target artifact, system, or dataset (e.g. "EV charger monitoring system", "application", "5 datasets").
5. domain: Industry or technical domain (e.g. "EV charging", "fintech", "distributed systems", "healthcare").
6. certainty: Epistemic certainty level or modality (e.g. "high", "low", "certain", "tentative", "possible", "definitely").
7. qualifier: Adjectives/adverbs describing complexity, novelty, or performance (e.g. "advanced", "cutting-edge", "state-of-the-art", "simple").
8. scope: Geographic, organizational, or operational scope (e.g. "global", "regional", "local", "enterprise-wide").
9. impact: Measured business, technical, or research impact (e.g. "improved efficiency", "reduced latency", "high impact").
10. quantitative_info: Numbers, metrics, percentages, sample sizes, durations (e.g. "5", "over 5", "100%", "10x", "5 years").

FEW-SHOT EXAMPLE:
Claim: "I helped analyze approximately 5 datasets."
Output:
{
  "subject_entity": {"value": "I", "confidence": 0.99},
  "role_agency": {"value": "assisted", "confidence": 0.95},
  "activity_action": {"value": "analyze", "confidence": 0.98},
  "object": {"value": "datasets", "confidence": 0.96},
  "domain": {"value": null, "confidence": 1.0},
  "certainty": {"value": "high", "confidence": 0.90},
  "qualifier": {"value": null, "confidence": 1.0},
  "scope": {"value": null, "confidence": 1.0},
  "impact": {"value": null, "confidence": 1.0},
  "quantitative_info": {"value": "approximately 5", "confidence": 0.97},
  "overall_confidence": 0.96
}

Return ONLY valid JSON with exactly the above structure.
"""

def _call_llm_api(prompt: str, system_prompt: str, model: str, api_key: str, temperature: float = 0.0) -> str:
    """
    Calls LLM API via standard HTTP request. Supports Gemini and OpenAI formats.
    Deterministic temperature = 0.0 by default.
    """
    import urllib.request
    import urllib.error

    # Detect API flavor based on model name or key format
    if "gemini" in model.lower() or api_key.startswith("AIza"):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": f"{system_prompt}\n\nInput:\n{prompt}"}]}],
            "generationConfig": {"temperature": temperature, "responseMimeType": "application/json"}
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
    else:
        # Default OpenAI-compatible endpoint
        url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1") + "/chat/completions"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"}
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            return res_json["choices"][0]["message"]["content"]


class LLMAtomicClaimExtractor(AtomicClaimExtractor):
    """
    Production atomic claim extractor. Calls LLM API if configured with deterministic
    temperature=0, or falls back to robust sentence-level span parsing when running offline.
    """

    def __init__(
        self,
        config: Optional[FactSculptConfig] = None,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.0
    ):
        self.config = config or FactSculptConfig()
        self.api_key = api_key or self.config.api_key or os.getenv("FACTSCULPT_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name or self.config.claim_extractor_model
        self.temperature = temperature

    def extract_claims(self, text: str) -> List[AtomicClaim]:
        if not text or not text.strip():
            return []

        if self.api_key:
            try:
                raw_out = _call_llm_api(
                    prompt=text,
                    system_prompt=EXTRACTION_SYSTEM_PROMPT,
                    model=self.model_name,
                    api_key=self.api_key,
                    temperature=self.temperature
                )
                data = json.loads(raw_out)
                claims_data = data.get("claims", [])
                claims = []
                for idx, c in enumerate(claims_data):
                    claim_text = c.get("text", "").strip()
                    if not claim_text:
                        continue
                    # Compute spans if missing
                    span_start = c.get("span_start")
                    span_end = c.get("span_end")
                    if span_start is None or span_end is None:
                        pos = text.find(claim_text)
                        if pos != -1:
                            span_start = pos
                            span_end = pos + len(claim_text)
                        else:
                            span_start = 0
                            span_end = len(text)
                    evidence_span = c.get("evidence_span", claim_text)
                    conf = float(c.get("confidence", 0.9))
                    claims.append(
                        AtomicClaim(
                            claim_id=f"claim_{idx}",
                            text=claim_text,
                            span_start=span_start,
                            span_end=span_end,
                            evidence_span=evidence_span,
                            confidence=conf
                        )
                    )
                if claims:
                    return claims
            except Exception as e:
                logger.warning(f"LLM claim extraction failed ({e}), falling back to heuristic parsing.")

        # Offline heuristic fallback
        return self._heuristic_extract(text)

    def _heuristic_extract(self, text: str) -> List[AtomicClaim]:
        claims = []
        pattern = re.compile(r"[^.!?]+(?:[.!?]+|$)")
        for match in pattern.finditer(text):
            sentence = match.group(0)
            span_start = match.start()
            span_end = match.end()

            left_strip_len = len(sentence) - len(sentence.lstrip())
            right_strip_len = len(sentence) - len(sentence.rstrip())

            clean_sentence = sentence.strip()
            if not clean_sentence:
                continue

            clean_start = span_start + left_strip_len
            clean_end = span_end - right_strip_len

            claims.append(
                AtomicClaim(
                    claim_id=f"claim_{len(claims)}",
                    text=clean_sentence,
                    span_start=clean_start,
                    span_end=clean_end,
                    evidence_span=clean_sentence,
                    confidence=1.0
                )
            )
        return claims


class LLMEvidenceProfileExtractor(EvidenceProfileExtractor):
    """
    Primary evidence profile extractor for FactSculpt.
    Uses structured LLM prompting with strict JSON schema (role_agency, qualifier, scope,
    certainty, impact, quantity), deterministic temperature=0, response caching,
    and attribute-level plus overall confidence scores.
    Falls back to RegexEvidenceProfileExtractor when running offline or without live API keys.
    """

    def __init__(
        self,
        config: Optional[FactSculptConfig] = None,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.0,
        cache: Optional[ProfileResponseCache] = None,
        fallback_extractor: Optional[EvidenceProfileExtractor] = None
    ):
        self.config = config or FactSculptConfig()
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = self.config.api_key or os.getenv("FACTSCULPT_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.model_name = model_name or self.config.profile_extractor_model
        self.temperature = temperature
        self.cache = cache if cache is not None else ProfileResponseCache()
        self.fallback_extractor = fallback_extractor if fallback_extractor is not None else RegexEvidenceProfileExtractor()
        self.cache_hits: int = 0
        self.cache_misses: int = 0

    def extract_profile(self, claim: AtomicClaim) -> EvidenceProfile:
        text = claim.text.strip()
        if not text:
            return EvidenceProfile()

        # 1. Check persistent response cache
        cached_data = self.cache.get(text, self.model_name)
        if cached_data is not None:
            self.cache_hits += 1
            return self._parse_profile_json(cached_data)

        self.cache_misses += 1

        # 2. Primary: Call live LLM with strict JSON schema and temperature=0
        if self.api_key:
            try:
                raw_out = _call_llm_api(
                    prompt=text,
                    system_prompt=PROFILE_SYSTEM_PROMPT,
                    model=self.model_name,
                    api_key=self.api_key,
                    temperature=self.temperature
                )
                data = json.loads(raw_out)
                profile = self._parse_profile_json(data)
                # Store in persistent cache
                self.cache.set(text, self.model_name, data)
                return profile
            except Exception as e:
                logger.warning(f"LLM evidence profile extraction failed ({e}), falling back to regex extractor.")

        # 3. Offline fallback: RegexEvidenceProfileExtractor
        fallback_profile = self.fallback_extractor.extract_profile(claim)
        # Store in cache so repeat offline requests are instant
        try:
            dumped = fallback_profile.model_dump()
            self.cache.set(text, self.model_name, dumped)
        except Exception:
            pass
        return fallback_profile

    def _parse_profile_json(self, data: Dict[str, Any]) -> EvidenceProfile:
        """
        Parses structured profile JSON, supporting both nested {value, confidence}
        objects and flat strings.
        """
        kwargs: Dict[str, Any] = {}
        confidences: Dict[str, float] = {}

        fields = [
            "role_agency", "activity_action", "object", "domain",
            "certainty", "qualifier", "scope", "impact", "quantitative_info",
            "subject_entity"
        ]

        for field in fields:
            val_obj = data.get(field)
            if isinstance(val_obj, dict):
                v = val_obj.get("value")
                c = float(val_obj.get("confidence", 0.9))
                kwargs[field] = v
                confidences[field] = c
            elif isinstance(val_obj, str):
                kwargs[field] = val_obj
                confidences[field] = 0.95
            else:
                kwargs[field] = None
                confidences[field] = 1.0

        overall_conf = float(data.get("overall_confidence", sum(confidences.values()) / max(len(confidences), 1)))
        return EvidenceProfile(
            **kwargs,
            attribute_confidences=confidences,
            overall_confidence=overall_conf
        )

    def _heuristic_profile(self, text: str) -> EvidenceProfile:
        """
        Generalized heuristic attribute extractor for offline execution.
        Extracts roles, qualifiers, scopes, certainty, impact, and quantities with confidence.
        """
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
            overall_confidence=overall
        )
