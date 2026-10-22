import math
from typing import Dict, List, Tuple, Optional, Any
from pydantic import BaseModel, Field

# Pairwise comparisons derived from evidence hierarchy in closed-world domains
SEED_PAIRWISE_COMPARISONS: Dict[str, List[Tuple[str, str]]] = {
    "role_agency": [
        ("assisted", "contributed"),
        ("contributed", "participated"),
        ("participated", "developed"),
        ("developed", "engineered"),
        ("engineered", "managed"),
        ("managed", "directed"),
        ("directed", "spearheaded"),
        ("spearheaded", "architected"),
        ("architected", "founded"),
        ("assisted", "led"),
        ("supported", "led"),
        ("helped", "owned"),
        ("shadowed", "assisted"),
        ("co-developed", "led")
    ],
    "qualifier": [
        ("simple", "standard"),
        ("basic", "standard"),
        ("standard", "modern"),
        ("modern", "advanced"),
        ("advanced", "scalable"),
        ("scalable", "sophisticated"),
        ("sophisticated", "cutting-edge"),
        ("cutting-edge", "state-of-the-art"),
        ("state-of-the-art", "industry-leading"),
        ("rudimentary", "advanced"),
        ("preliminary", "production-ready")
    ],
    "scope": [
        ("local", "regional"),
        ("regional", "national"),
        ("national", "enterprise-wide"),
        ("enterprise-wide", "global"),
        ("global", "worldwide"),
        ("branch", "company-wide"),
        ("single-team", "cross-functional")
    ],
    "certainty": [
        ("tentative", "possible"),
        ("possibly", "likely"),
        ("might", "probably"),
        ("could", "will"),
        ("likely", "certain"),
        ("probable", "definitely"),
        ("may", "guaranteed"),
        ("low", "moderate"),
        ("moderate", "high")
    ],
    "impact": [
        ("negligible", "minimal"),
        ("minimal", "moderate"),
        ("slight", "noticeable"),
        ("moderate", "significant"),
        ("noticeable", "improved efficiency"),
        ("significant", "high impact"),
        ("improved efficiency", "massive improvement"),
        ("high impact", "transformational")
    ],
    "quantitative_info": [
        ("few", "several"),
        ("approximately 5", "5"),
        ("5", "over 5"),
        ("over 5", "10"),
        ("10", "over 10"),
        ("50%", "75%"),
        ("75%", "100%"),
        ("some", "most"),
        ("most", "all")
    ]
}

class OrdinalScaleParameters(BaseModel):
    attribute_name: str
    item_strengths: Dict[str, float] = Field(default_factory=dict)
    mean_strength: float = 0.0
    scale_type: str = "bradley_terry"

class BradleyTerryOrdinalScaler:
    """
    Learns continuous ordinal scales for evidential attributes using the Bradley-Terry
    probabilistic preference model:
      P(w_B > w_A) = 1 / (1 + exp(-(lambda_B - lambda_A)))
    
    Trained via iterative cross-entropy / MM algorithm on pairwise comparisons.
    Produces a continuous signed magnitude shift in [-1.0, +1.0]:
      shift(src, gen) = tanh(lambda_gen - lambda_src)
    """

    def __init__(self, learning_rate: float = 0.1, max_iter: int = 150):
        self.learning_rate = learning_rate
        self.max_iter = max_iter
        self.scales: Dict[str, OrdinalScaleParameters] = {}
        # Train immediately on seed pairwise comparisons
        self.fit_seed_scales()

    def fit_attribute_scale(
        self,
        attribute_name: str,
        pairwise_pairs: List[Tuple[str, str]]
    ) -> OrdinalScaleParameters:
        """
        Fits Bradley-Terry parameters where each tuple is (weaker, stronger).
        """
        # Collect vocabulary of items
        items = sorted(list({item for pair in pairwise_pairs for item in pair}))
        if not items:
            return OrdinalScaleParameters(attribute_name=attribute_name)

        item_idx = {item: i for i, item in enumerate(items)}
        n = len(items)

        # Log-strengths lambda initialized to 0.0
        lambdas = [0.0] * n

        # Gradient descent on negative log likelihood
        for _ in range(self.max_iter):
            grad = [0.0] * n
            for weaker, stronger in pairwise_pairs:
                w_i = item_idx[weaker]
                s_i = item_idx[stronger]

                # P(stronger > weaker) = sigmoid(lambda_s - lambda_w)
                diff = lambdas[s_i] - lambdas[w_i]
                p_win = 1.0 / (1.0 + math.exp(-max(min(diff, 20.0), -20.0)))

                # Gradient
                error = 1.0 - p_win
                grad[s_i] += error
                grad[w_i] -= error

            # Update with L2 regularization
            for i in range(n):
                lambdas[i] += self.learning_rate * (grad[i] - 0.01 * lambdas[i])

        # Anchor median/mean to 0.0
        mean_val = sum(lambdas) / n
        strengths = {item: round(lambdas[i] - mean_val, 4) for item, i in item_idx.items()}

        param = OrdinalScaleParameters(
            attribute_name=attribute_name,
            item_strengths=strengths,
            mean_strength=0.0
        )
        self.scales[attribute_name] = param
        return param

    def fit_seed_scales(self):
        """Fits scales for all 6 evidential attributes from seed comparisons."""
        for attr, pairs in SEED_PAIRWISE_COMPARISONS.items():
            self.fit_attribute_scale(attr, pairs)

    def score_shift(
        self,
        attribute_name: str,
        src_val: Optional[str],
        gen_val: Optional[str]
    ) -> float:
        """
        Calculates continuous signed magnitude shift in [-1.0, 1.0]:
        positive = strengthening, negative = weakening, 0 = unchanged.
        """
        if not src_val and not gen_val:
            return 0.0
        if not src_val and gen_val:
            return 0.75  # Addition of attribute
        if src_val and not gen_val:
            return -0.75  # Removal of attribute

        src_clean = src_val.strip().lower()
        gen_clean = gen_val.strip().lower()

        if src_clean == gen_clean:
            return 0.0

        scale = self.scales.get(attribute_name)
        if not scale or not scale.item_strengths:
            # Fallback to normalized heuristic
            return 0.0

        # Exact match or substring matching in item strengths
        src_str = self._lookup_strength(scale, src_clean)
        gen_str = self._lookup_strength(scale, gen_clean)

        if src_str is None or gen_str is None:
            return 0.0

        # Continuous magnitude via tanh
        delta = gen_str - src_str
        return round(math.tanh(delta), 4)

    def _lookup_strength(self, scale: OrdinalScaleParameters, text: str) -> Optional[float]:
        if text in scale.item_strengths:
            return scale.item_strengths[text]
        # Partial match
        for k, v in scale.item_strengths.items():
            if k in text or text in k:
                return v
        return None
