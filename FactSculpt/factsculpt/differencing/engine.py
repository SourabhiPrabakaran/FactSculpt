import re
from typing import Optional, Dict, Any, Tuple
from factsculpt.models import AtomicClaim
from factsculpt.differencing.interfaces import AttributeDifferencer
from factsculpt.differencing.models import (
    ChangeType,
    Direction,
    ProfileStatus,
    AttributeDelta,
    AttributeDifferenceResult,
    VALID_ATTRIBUTES,
)

def normalize(val: Optional[str]) -> Optional[str]:
    """
    Normalizes a text value for comparison:
    - Lowercase
    - Strip leading/trailing whitespace
    - Collapse repeated whitespace to a single space
    """
    if val is None:
        return None
    cleaned = val.strip().lower()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned if cleaned else None

def _extract_number(val: Optional[str]) -> Optional[float]:
    if not val:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)", val)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None

class AttributeDifferenceEngine(AttributeDifferencer):
    """
    Deterministic comparison engine that compares two AtomicClaims' EvidenceProfiles.
    Detects all evidence strengthening and weakening signals across:
    - role_agency (role)
    - qualifier
    - scope
    - certainty
    - impact
    - quantitative_info (quantity)

    Produces both discrete AttributeDelta objects and a 6-attribute continuous signed shift vector:
    {
      "role": float,
      "qualifier": float,
      "scope": float,
      "certainty": float,
      "impact": float,
      "quantity": float
    }
    where negative = weakening, zero = unchanged, positive = strengthening.
    """

    DEFAULT_SEVERITY_WEIGHTS = {
        "role": 0.25,
        "qualifier": 0.15,
        "scope": 0.20,
        "certainty": 0.15,
        "impact": 0.15,
        "quantity": 0.10
    }

    def __init__(
        self,
        ordinal_scaler: Optional[Any] = None,
        severity_weights: Optional[Dict[str, float]] = None
    ):
        self.ordinal_scaler = ordinal_scaler
        self.severity_weights = severity_weights or dict(self.DEFAULT_SEVERITY_WEIGHTS)

    def compare(
        self,
        source_claim: AtomicClaim,
        generated_claim: AtomicClaim
    ) -> AttributeDifferenceResult:
        
        # 1. Handle missing profiles
        src_profile = source_claim.profile
        gen_profile = generated_claim.profile

        if src_profile is None and gen_profile is None:
            status = ProfileStatus.BOTH_PROFILES_MISSING
        elif src_profile is None:
            status = ProfileStatus.PROFILE_MISSING_SOURCE
        elif gen_profile is None:
            status = ProfileStatus.PROFILE_MISSING_GENERATED
        else:
            status = ProfileStatus.PROFILE_AVAILABLE

        # Return immediately if one or both profiles are missing
        if status != ProfileStatus.PROFILE_AVAILABLE:
            empty_vector = {k: 0.0 for k in ["role", "qualifier", "scope", "certainty", "impact", "quantity"]}
            return AttributeDifferenceResult(
                source_claim_id=source_claim.claim_id,
                generated_claim_id=generated_claim.claim_id,
                profile_status=status,
                deltas=[],
                shift_vector=empty_vector,
                severity=0.0
            )

        # Discrete dictionaries for fallback heuristic ranking
        weak_roles = {"assisted", "supported", "participated", "contributed", "helped", "shadowed"}
        strong_roles = {"led", "directed", "managed", "spearheaded", "founded", "architected", "owned"}

        strengthening_qualifiers = {
            "advanced", "sophisticated", "cutting-edge", "highly efficient",
            "state-of-the-art", "modern", "complex", "scalable", "industry-leading",
            "mission-critical", "robust"
        }
        weakening_qualifiers = {"simple", "basic", "toy", "rudimentary", "preliminary"}

        scope_ranks = {
            "local": 1,
            "regional": 2,
            "national": 3,
            "enterprise-wide": 3.5,
            "global": 4,
            "worldwide": 4
        }

        certainty_high = {"high", "definitely", "certain", "guaranteed", "always", "proved", "confirmed", "will"}
        certainty_low = {"low", "possibly", "might", "maybe", "tentative", "tentatively", "preliminary", "exploratory", "perhaps", "could", "may"}

        impact_high = {"high impact", "improved efficiency", "massive improvement", "massive", "huge", "tremendous", "significant", "transformational", "optimized performance"}
        impact_low = {"low impact", "low", "minimal", "negligible", "minor impact", "slight", "modest", "marginal"}

        deltas = []
        shift_vector = {
            "role": 0.0,
            "qualifier": 0.0,
            "scope": 0.0,
            "certainty": 0.0,
            "impact": 0.0,
            "quantity": 0.0
        }

        # 2. Compare each of the 9 defined profile attributes
        for attr in sorted(VALID_ATTRIBUTES):
            src_val = getattr(src_profile, attr)
            gen_val = getattr(gen_profile, attr)

            src_norm = normalize(src_val)
            gen_norm = normalize(gen_val)

            # Determine ChangeType
            if src_norm is None and gen_norm is None:
                change_type = ChangeType.UNCHANGED
            elif src_norm is None and gen_norm is not None:
                change_type = ChangeType.ADDED
            elif src_norm is not None and gen_norm is None:
                change_type = ChangeType.REMOVED
            elif src_norm == gen_norm:
                change_type = ChangeType.UNCHANGED
            else:
                change_type = ChangeType.MODIFIED

            # Determine Direction and Shift Value
            direction = Direction.UNCHANGED

            if change_type != ChangeType.UNCHANGED:
                direction = Direction.CHANGED

                # Use learned ordinal scaler if available
                if self.ordinal_scaler is not None and hasattr(self.ordinal_scaler, "score_shift"):
                    shift_val = self.ordinal_scaler.score_shift(attr, src_val, gen_val)
                else:
                    shift_val = None

                if attr == "role_agency":
                    if shift_val is not None:
                        shift_vector["role"] = shift_val
                        if shift_val > 0.05:
                            direction = Direction.STRENGTHENED
                        elif shift_val < -0.05:
                            direction = Direction.WEAKENED
                    elif change_type == ChangeType.MODIFIED:
                        if src_norm in weak_roles and gen_norm in strong_roles:
                            direction = Direction.STRENGTHENED
                            shift_vector["role"] = 1.0
                        elif src_norm in strong_roles and gen_norm in weak_roles:
                            direction = Direction.WEAKENED
                            shift_vector["role"] = -1.0
                    elif change_type == ChangeType.ADDED:
                        if gen_norm in strong_roles:
                            direction = Direction.STRENGTHENED
                            shift_vector["role"] = 0.8
                    elif change_type == ChangeType.REMOVED:
                        if src_norm in strong_roles:
                            direction = Direction.WEAKENED
                            shift_vector["role"] = -0.8

                elif attr == "qualifier":
                    if shift_val is not None:
                        shift_vector["qualifier"] = shift_val
                        if shift_val > 0.05:
                            direction = Direction.STRENGTHENED
                        elif shift_val < -0.05:
                            direction = Direction.WEAKENED
                    elif change_type == ChangeType.ADDED:
                        if gen_norm in strengthening_qualifiers:
                            direction = Direction.STRENGTHENED
                            shift_vector["qualifier"] = 1.0
                        elif gen_norm in weakening_qualifiers:
                            direction = Direction.WEAKENED
                            shift_vector["qualifier"] = -1.0
                        else:
                            shift_vector["qualifier"] = 0.5
                    elif change_type == ChangeType.REMOVED:
                        if src_norm in strengthening_qualifiers:
                            direction = Direction.WEAKENED
                            shift_vector["qualifier"] = -1.0
                        elif src_norm in weakening_qualifiers:
                            direction = Direction.STRENGTHENED
                            shift_vector["qualifier"] = 0.5
                        else:
                            shift_vector["qualifier"] = -0.5
                    elif change_type == ChangeType.MODIFIED:
                        if src_norm in weakening_qualifiers and gen_norm in strengthening_qualifiers:
                            direction = Direction.STRENGTHENED
                            shift_vector["qualifier"] = 1.0
                        elif src_norm in strengthening_qualifiers and gen_norm in weakening_qualifiers:
                            direction = Direction.WEAKENED
                            shift_vector["qualifier"] = -1.0

                elif attr == "scope":
                    if shift_val is not None:
                        shift_vector["scope"] = shift_val
                        if shift_val > 0.05:
                            direction = Direction.EXPANDED
                        elif shift_val < -0.05:
                            direction = Direction.REDUCED
                    elif change_type == ChangeType.MODIFIED:
                        if src_norm in scope_ranks and gen_norm in scope_ranks:
                            if scope_ranks[gen_norm] > scope_ranks[src_norm]:
                                direction = Direction.EXPANDED
                                diff = (scope_ranks[gen_norm] - scope_ranks[src_norm]) / 3.0
                                shift_vector["scope"] = min(diff, 1.0)
                            elif scope_ranks[gen_norm] < scope_ranks[src_norm]:
                                direction = Direction.REDUCED
                                diff = (scope_ranks[src_norm] - scope_ranks[gen_norm]) / 3.0
                                shift_vector["scope"] = -min(diff, 1.0)
                    elif change_type == ChangeType.ADDED:
                        direction = Direction.EXPANDED
                        shift_vector["scope"] = 0.7
                    elif change_type == ChangeType.REMOVED:
                        direction = Direction.REDUCED
                        shift_vector["scope"] = -0.7

                elif attr == "certainty":
                    if shift_val is not None:
                        shift_vector["certainty"] = shift_val
                        if shift_val > 0.05:
                            direction = Direction.STRENGTHENED
                        elif shift_val < -0.05:
                            direction = Direction.WEAKENED
                    elif change_type == ChangeType.MODIFIED:
                        is_src_low = src_norm in certainty_low or "low" in (src_norm or "") or "might" in (src_norm or "") or "possibly" in (src_norm or "")
                        is_gen_high = gen_norm in certainty_high or "high" in (gen_norm or "") or "definitely" in (gen_norm or "") or "certain" in (gen_norm or "")
                        is_src_high = src_norm in certainty_high or "high" in (src_norm or "") or "definitely" in (src_norm or "")
                        is_gen_low = gen_norm in certainty_low or "low" in (gen_norm or "") or "might" in (gen_norm or "")

                        if is_src_low and is_gen_high:
                            direction = Direction.STRENGTHENED
                            shift_vector["certainty"] = 1.0
                        elif is_src_high and is_gen_low:
                            direction = Direction.WEAKENED
                            shift_vector["certainty"] = -1.0
                    elif change_type == ChangeType.ADDED:
                        if gen_norm in certainty_high:
                            direction = Direction.STRENGTHENED
                            shift_vector["certainty"] = 0.8
                    elif change_type == ChangeType.REMOVED:
                        if src_norm in certainty_high:
                            direction = Direction.WEAKENED
                            shift_vector["certainty"] = -0.8

                elif attr == "impact":
                    if shift_val is not None:
                        shift_vector["impact"] = shift_val
                        if shift_val > 0.05:
                            direction = Direction.STRENGTHENED
                        elif shift_val < -0.05:
                            direction = Direction.WEAKENED
                    elif change_type == ChangeType.MODIFIED:
                        is_src_low = src_norm in impact_low or "low" in (src_norm or "")
                        is_gen_high = gen_norm in impact_high or "high" in (gen_norm or "") or "improved" in (gen_norm or "")
                        is_src_high = src_norm in impact_high or "high" in (src_norm or "") or "improved" in (src_norm or "")
                        is_gen_low = gen_norm in impact_low or "low" in (gen_norm or "")

                        if is_src_low and is_gen_high:
                            direction = Direction.STRENGTHENED
                            shift_vector["impact"] = 1.0
                        elif is_src_high and is_gen_low:
                            direction = Direction.WEAKENED
                            shift_vector["impact"] = -1.0
                    elif change_type == ChangeType.ADDED:
                        if gen_norm in impact_high:
                            direction = Direction.STRENGTHENED
                            shift_vector["impact"] = 0.8
                    elif change_type == ChangeType.REMOVED:
                        if src_norm in impact_high:
                            direction = Direction.WEAKENED
                            shift_vector["impact"] = -0.8

                elif attr == "quantitative_info":
                    if shift_val is not None:
                        shift_vector["quantity"] = shift_val
                        if shift_val > 0.05:
                            direction = Direction.STRENGTHENED
                        elif shift_val < -0.05:
                            direction = Direction.WEAKENED
                    else:
                        src_num = _extract_number(src_norm)
                        gen_num = _extract_number(gen_norm)
                        # Check bounded vs unbounded ("about 5" -> "over 5")
                        has_over = gen_norm and ("over" in gen_norm or "more than" in gen_norm or "at least" in gen_norm)
                        has_about = src_norm and ("about" in src_norm or "approx" in src_norm or "helped" in src_norm)

                        if has_about and has_over:
                            direction = Direction.STRENGTHENED
                            shift_vector["quantity"] = 0.75
                        elif src_num is not None and gen_num is not None:
                            if gen_num > src_num:
                                direction = Direction.STRENGTHENED
                                rel = (gen_num - src_num) / max(src_num, 1.0)
                                shift_vector["quantity"] = min(rel, 1.0)
                            elif gen_num < src_num:
                                direction = Direction.WEAKENED
                                rel = (src_num - gen_num) / max(src_num, 1.0)
                                shift_vector["quantity"] = -min(rel, 1.0)
                        elif change_type == ChangeType.ADDED:
                            direction = Direction.STRENGTHENED
                            shift_vector["quantity"] = 0.5
                        elif change_type == ChangeType.REMOVED:
                            direction = Direction.WEAKENED
                            shift_vector["quantity"] = -0.5

            # Append delta using the original unnormalized values
            deltas.append(
                AttributeDelta(
                    attribute_name=attr,
                    source_value=src_val,
                    generated_value=gen_val,
                    change_type=change_type,
                    direction=direction,
                )
            )

        # Calculate overall severity score
        # severity = sum(weight_attribute * abs(attribute_shift))
        total_sev = 0.0
        for k, v in shift_vector.items():
            w = self.severity_weights.get(k, 0.15)
            total_sev += w * abs(v)
        severity = round(min(total_sev, 1.0), 4)

        return AttributeDifferenceResult(
            source_claim_id=source_claim.claim_id,
            generated_claim_id=generated_claim.claim_id,
            profile_status=status,
            deltas=deltas,
            shift_vector=shift_vector,
            severity=severity
        )
