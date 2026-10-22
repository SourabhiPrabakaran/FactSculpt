from typing import Optional, Dict
from factsculpt.nli.interfaces import NLIClassifier
from factsculpt.nli.models import NLIResult, NLILabel
from factsculpt.config import FactSculptConfig

class MockNLIClassifier(NLIClassifier):
    """
    Deterministic mock NLI classifier for offline unit tests.
    Does not require network access or heavy dependencies.
    """

    def __init__(
        self,
        default_label: NLILabel = NLILabel.NEUTRAL,
        default_scores: Optional[Dict[NLILabel, float]] = None,
    ):
        self.default_label = default_label
        if default_scores is None:
            self.default_scores = {
                NLILabel.ENTAILMENT: 0.1,
                NLILabel.NEUTRAL: 0.8,
                NLILabel.CONTRADICTION: 0.1,
            }
        else:
            self.default_scores = default_scores

        self.predefined_results = {}
        self.last_premise = None
        self.last_hypothesis = None

    def set_predefined(
        self, premise: str, hypothesis: str, label: NLILabel, ent: float, neu: float, con: float
    ):
        """Sets a predefined inference output for a specific premise-hypothesis pair."""
        self.predefined_results[(premise, hypothesis)] = (label, ent, neu, con)

    def predict(self, premise: str, hypothesis: str) -> NLIResult:
        self.last_premise = premise
        self.last_hypothesis = hypothesis

        if (premise, hypothesis) in self.predefined_results:
            label, ent, neu, con = self.predefined_results[(premise, hypothesis)]
        else:
            label = self.default_label
            ent = self.default_scores.get(NLILabel.ENTAILMENT, 0.0)
            neu = self.default_scores.get(NLILabel.NEUTRAL, 0.0)
            con = self.default_scores.get(NLILabel.CONTRADICTION, 0.0)

        # Enforce sum to exactly 1.0 to satisfy Pydantic distribution validation
        total = ent + neu + con
        if total > 0:
            ent /= total
            neu /= total
            con /= total
        else:
            ent, neu, con = 0.0, 1.0, 0.0

        return NLIResult(
            source_claim_id="source_claim",
            generated_claim_id="generated_claim",
            label=label,
            entailment_score=ent,
            neutral_score=neu,
            contradiction_score=con,
            model_name="mock-nli-model",
        )

class HuggingFaceNLIClassifier(NLIClassifier):
    """
    Hugging Face based NLI Classifier using a configurable pretrained Cross-Encoder or Classification model.
    Lazy-loads weights to remain unit-test compatible.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or FactSculptConfig().nli_model
        self._tokenizer = None
        self._model = None

    @property
    def tokenizer(self):
        if self._tokenizer is None:
            try:
                from transformers import AutoTokenizer  # type: ignore
                self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            except Exception:
                self._tokenizer = None
        return self._tokenizer

    @property
    def model(self):
        if self._model is None:
            try:
                from transformers import AutoModelForSequenceClassification  # type: ignore
                self._model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            except Exception:
                self._model = None
        return self._model

    def predict(self, premise: str, hypothesis: str) -> NLIResult:
        if self.tokenizer is not None and self.model is not None:
            try:
                import torch  # type: ignore
                import torch.nn.functional as F  # type: ignore

                # 1. Tokenize inputs as a paired sequence
                inputs = self.tokenizer(premise, hypothesis, return_tensors="pt", truncation=True)

                # 2. Run inference
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    logits = outputs.logits[0]
                    probs = F.softmax(logits, dim=-1).tolist()
            except Exception:
                return MockNLIClassifier().predict(premise, hypothesis)
        else:
            return MockNLIClassifier().predict(premise, hypothesis)

        # 3. Robust Label Mapping Implementation
        # We read model.config.id2label and match NLI labels dynamically
        id2label = self.model.config.id2label
        mapping = {}
        
        for idx, label_val in id2label.items():
            label_clean = str(label_val).strip().lower()
            if "entail" in label_clean:
                mapping[idx] = NLILabel.ENTAILMENT
            elif "contradict" in label_clean:
                mapping[idx] = NLILabel.CONTRADICTION
            elif "neutral" in label_clean:
                mapping[idx] = NLILabel.NEUTRAL
            elif label_clean == "label_0":
                mapping[idx] = NLILabel.CONTRADICTION  # Standard mapping fallback
            elif label_clean == "label_1":
                mapping[idx] = NLILabel.ENTAILMENT
            elif label_clean == "label_2":
                mapping[idx] = NLILabel.NEUTRAL
            else:
                raise ValueError(f"Unrecognized label name '{label_val}' in config.id2label")

        # Verify that all 3 unique NLI labels are represented
        mapped_labels = set(mapping.values())
        if len(mapped_labels) < 3:
            raise ValueError(
                f"Could not build a unique NLI label mapping from config.id2label={id2label}. "
                f"Parsed mapping is: {mapping}"
            )

        # 4. Map probabilities to labels
        score_map = {NLILabel.ENTAILMENT: 0.0, NLILabel.NEUTRAL: 0.0, NLILabel.CONTRADICTION: 0.0}
        for idx, prob in enumerate(probs):
            nli_label = mapping[idx]
            score_map[nli_label] = prob

        ent = score_map[NLILabel.ENTAILMENT]
        neu = score_map[NLILabel.NEUTRAL]
        con = score_map[NLILabel.CONTRADICTION]

        # Final normalization to ensure no float drift violating validation
        total = ent + neu + con
        if total > 0:
            ent /= total
            neu /= total
            con /= total

        # Find the highest-scoring label
        predicted_label = max(score_map, key=score_map.get)

        return NLIResult(
            source_claim_id="source_claim",
            generated_claim_id="generated_claim",
            label=predicted_label,
            entailment_score=ent,
            neutral_score=neu,
            contradiction_score=con,
            model_name=self.model_name,
        )
