import os
import pickle
import numpy as np
from typing import List, Dict, Optional, Any, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV

from factsculpt.features.models import EvidenceDeviationFeatures
from factsculpt.classifier.interfaces import ClassifierInterface
from factsculpt.classifier.models import (
    ClassificationCode,
    RESEARCH_CLASSIFICATION_NAMES,
    ClassificationResult,
)
from factsculpt.dataset.schema import PairExample, MainClass

def compute_ece(probs: np.ndarray, y_true: np.ndarray, n_bins: int = 10) -> float:
    """
    Computes Expected Calibration Error (ECE) for multi-class predictions.
    ECE = sum_{m=1}^M (|B_m| / N) * |acc(B_m) - conf(B_m)|
    """
    if len(probs) == 0:
        return 0.0

    preds = np.argmax(probs, axis=1)
    confs = np.max(probs, axis=1)
    accuracies = (preds == y_true)

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    n = len(y_true)

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]

        in_bin = (confs > bin_lower) & (confs <= bin_upper)
        prop_in_bin = np.mean(in_bin)

        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(accuracies[in_bin])
            avg_confidence_in_bin = np.mean(confs[in_bin])
            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin

    return round(float(ece), 4)

class LearnedExaggerationClassifier(ClassifierInterface):
    """
    Learned machine-learning classifier for Closed-World Evidence Exaggeration Detection.
    Supports Logistic Regression and Gradient Boosted Decision Trees (GBDT)
    with probability calibration (Platt scaling) and abstention decision logic.
    """

    CLASS_LIST = ["C1", "C2", "C3", "C4", "C5"]

    def __init__(
        self,
        model_type: str = "gradient_boosting",
        abstention_threshold: float = 0.40,
        random_state: int = 42
    ):
        self.model_type = model_type.lower()
        self.abstention_threshold = abstention_threshold
        self.random_state = random_state

        if self.model_type in ("logistic_regression", "logreg"):
            base_estimator = LogisticRegression(
                max_iter=1000,
                random_state=random_state,
                C=1.0
            )

        else:
            base_estimator = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=4,
                random_state=random_state
            )

        self.model = base_estimator
        self.calibrated_model: Optional[CalibratedClassifierCV] = None
        self.is_fitted = False
        self.ece_score: Optional[float] = None

    def fit(self, X: np.ndarray, y: np.ndarray, X_val: Optional[np.ndarray] = None, y_val: Optional[np.ndarray] = None):
        """
        Fits the learned model and performs probability calibration.
        Evaluates ECE on validation set if provided.
        """
        self.model.fit(X, y)
        self.is_fitted = True

        # Fit probability calibrator
        try:
            self.calibrated_model = CalibratedClassifierCV(self.model, method="sigmoid", cv="prefit")
            if X_val is not None and y_val is not None:
                self.calibrated_model.fit(X_val, y_val)
                val_probs = self.calibrated_model.predict_proba(X_val)
                self.ece_score = compute_ece(val_probs, y_val)
            else:
                self.calibrated_model.fit(X, y)
                probs = self.calibrated_model.predict_proba(X)
                self.ece_score = compute_ece(probs, y)
        except Exception:
            # Fallback to direct model probabilities if cv='prefit' is unsupported
            self.calibrated_model = None
            if hasattr(self.model, "predict_proba"):
                eval_X = X_val if X_val is not None else X
                eval_y = y_val if y_val is not None else y
                probs = self.model.predict_proba(eval_X)
                self.ece_score = compute_ece(probs, eval_y)
            else:
                self.ece_score = None

    def fit_from_dataset(
        self,
        train_pairs: List[PairExample],
        val_pairs: Optional[List[PairExample]] = None,
        use_predicted_extraction: bool = False
    ):
        """
        Convenience training method directly consuming PairExample datasets.
        """
        from factsculpt.features.extraction import extract_pair_features

        def extract_features_and_labels(pairs: List[PairExample]) -> Tuple[np.ndarray, np.ndarray]:
            X_list = []
            y_list = []
            cat_map = {"C1": 0, "C2": 1, "C3": 2, "C4": 3, "C5": 4}

            for p in pairs:
                feats = extract_pair_features(p, use_predicted_extraction=use_predicted_extraction)
                X_list.append(feats.to_feature_vector())
                y_list.append(cat_map[p.main_class.value])

            return np.array(X_list, dtype=np.float32), np.array(y_list, dtype=np.int32)

        for p in train_pairs:
            if getattr(p, "provenance", None) == "system":
                raise ValueError(
                    f"Refusing 'system' provenance label as ground truth for training (example_id={p.example_id}). "
                    "Hard Rule 2: Never use system's own predictions as ground truth for training or evaluation."
                )
        if val_pairs:
            for p in val_pairs:
                if getattr(p, "provenance", None) == "system":
                    raise ValueError(
                        f"Refusing 'system' provenance label as ground truth for validation (example_id={p.example_id}). "
                        "Hard Rule 2: Never use system's own predictions as ground truth for training or evaluation."
                    )

        X_train, y_train = extract_features_and_labels(train_pairs)
        if val_pairs:
            X_val, y_val = extract_features_and_labels(val_pairs)
        else:
            X_val, y_val = None, None

        self.fit(X_train, y_train, X_val, y_val)

    def classify(self, features: EvidenceDeviationFeatures) -> ClassificationResult:
        """
        Classifies an input EvidenceDeviationFeatures instance.
        """
        x_vec = np.array([features.to_feature_vector()], dtype=np.float32)

        if not self.is_fitted:
            # Fallback to rule-based prediction if unfitted
            from factsculpt.classifier.rules import RuleBasedExaggerationClassifier
            clf = RuleBasedExaggerationClassifier(taxonomy="research")
            return clf.classify(features)

        # Predict probabilities
        if self.calibrated_model is not None:
            probs = self.calibrated_model.predict_proba(x_vec)[0]
        else:
            probs = self.model.predict_proba(x_vec)[0]

        # Handle models fitted with fewer classes
        prob_dict = {}
        classes_present = getattr(self.model, "classes_", [0, 1, 2, 3, 4])
        for idx, cls_code in enumerate(self.CLASS_LIST):
            if idx in classes_present:
                pos = list(classes_present).index(idx)
                prob_dict[cls_code] = round(float(probs[pos]), 4)
            else:
                prob_dict[cls_code] = 0.0

        # Normalization
        tot = sum(prob_dict.values())
        if tot > 0:
            prob_dict = {k: round(v / tot, 4) for k, v in prob_dict.items()}

        best_class_code_str = max(prob_dict, key=prob_dict.get)
        confidence = prob_dict[best_class_code_str]
        code = ClassificationCode(best_class_code_str)
        name = RESEARCH_CLASSIFICATION_NAMES[code]

        # Abstention decision
        abstain = confidence < self.abstention_threshold

        # Reasons
        reasons = [
            f"learned classifier ({self.model_type}) predicted {code.value} with confidence {confidence * 100:.1f}%",
            f"top probability distribution: {prob_dict}"
        ]

        # Severity
        total_sev = sum(abs(v) for v in features.shift_vector.values()) * 0.2
        severity = round(min(total_sev, 1.0), 4)

        return ClassificationResult(
            source_claim_id=features.source_claim_id,
            generated_claim_id=features.generated_claim_id,
            classification_code=code,
            classification_name=name,
            confidence=confidence,
            reasons=reasons,
            shift_vector=features.shift_vector,
            severity=severity,
            probabilities=prob_dict,
            abstain=abstain,
            attribute_agreement_score=features.attribute_agreement_score
        )
