from pathlib import Path
import numpy as np
import joblib

from .training import train_classifier


class ComplaintClassifier:
    def __init__(self, artifact_dir: Path, training_data: Path):
        self.artifact_dir = Path(artifact_dir)
        self.training_data = Path(training_data)
        self.model_path = self.artifact_dir / "complaint_classifier.joblib"
        self._model = None

    def _load(self):
        if self._model is None:
            if not self.model_path.exists():
                train_classifier(self.training_data, self.artifact_dir)
            self._model = joblib.load(self.model_path)
        return self._model

    @property
    def classes(self):
        model = self._load()
        return list(model.named_steps["classifier"].classes_)

    def predict(self, text: str) -> dict:
        model = self._load()
        probs = model.predict_proba([text])[0]
        classes = model.named_steps["classifier"].classes_
        order = np.argsort(probs)[::-1]
        top = [
            {"label": str(classes[i]), "score": round(float(probs[i]), 4)}
            for i in order[:3]
        ]
        return {
            "label": top[0]["label"],
            "confidence": top[0]["score"],
            "top_predictions": top,
            "backend": "tfidf_logistic_regression",
        }

    def explain(self, text: str, predicted_label: str, top_n: int = 8) -> dict:
        model = self._load()
        vectorizer = model.named_steps["tfidf"]
        clf = model.named_steps["classifier"]
        vector = vectorizer.transform([text])
        feature_names = np.asarray(vectorizer.get_feature_names_out())
        class_index = list(clf.classes_).index(predicted_label)

        # Multiclass logistic regression has one coefficient row per class.
        coef = clf.coef_[class_index]
        values = vector.toarray()[0]
        contributions = values * coef
        nonzero = np.where(values > 0)[0]
        ranked = nonzero[np.argsort(contributions[nonzero])[::-1]] if len(nonzero) else []
        cues = [
            {
                "token": str(feature_names[i]),
                "contribution": round(float(contributions[i]), 4),
            }
            for i in ranked[:top_n]
            if contributions[i] > 0
        ]
        return {
            "method": "linear_feature_contribution",
            "explained_label": predicted_label,
            "top_positive_cues": cues,
            "caution": "These are local feature contributions from the supervised linear classifier, not causal explanations.",
        }
