from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


def train_intent_classifier(data_path: Path, artifact_dir: Path) -> dict:
    data_path = Path(data_path)
    artifact_dir = Path(artifact_dir)

    if not data_path.exists():
        raise FileNotFoundError(f"Bitext dataset not found: {data_path}")

    df = pd.read_csv(data_path).dropna(subset=["instruction", "intent"])
    df["instruction"] = df["instruction"].astype(str).str.strip()
    df["intent"] = df["intent"].astype(str).str.strip()
    df = df[(df["instruction"].str.len() >= 3) & df["intent"].ne("")]

    X_train, X_test, y_train, y_test = train_test_split(
        df["instruction"],
        df["intent"],
        test_size=0.20,
        random_state=42,
        stratify=df["intent"],
    )

    model = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    stop_words="english",
                    ngram_range=(1, 2),
                    min_df=2,
                    max_features=40000,
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=42,
                    solver="lbfgs",
                ),
            ),
        ]
    )

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    classes = [str(value) for value in model.named_steps["classifier"].classes_]

    metrics = {
        "dataset": "Bitext Customer Support Training Dataset",
        "dataset_rows": int(len(df)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "macro_precision": round(
            float(precision_score(y_test, predictions, average="macro", zero_division=0)), 4
        ),
        "macro_recall": round(
            float(recall_score(y_test, predictions, average="macro", zero_division=0)), 4
        ),
        "macro_f1": round(
            float(f1_score(y_test, predictions, average="macro", zero_division=0)), 4
        ),
        "classes": classes,
        "classification_report": classification_report(
            y_test, predictions, output_dict=True, zero_division=0
        ),
        "confusion_matrix": confusion_matrix(
            y_test, predictions, labels=classes
        ).tolist(),
        "note": (
            "Bitext is a curated hybrid synthetic dataset. Results may not "
            "generalise perfectly to real customer complaints."
        ),
    }

    artifact_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, artifact_dir / "intent_classifier.joblib")
    (artifact_dir / "intent_metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    return metrics


class IntentClassifier:
    def __init__(self, artifact_dir: Path, training_data: Path):
        self.artifact_dir = Path(artifact_dir)
        self.training_data = Path(training_data)
        self.model_path = self.artifact_dir / "intent_classifier.joblib"
        self._model = None

    def _load(self):
        if self._model is None:
            if not self.model_path.exists():
                train_intent_classifier(self.training_data, self.artifact_dir)
            self._model = joblib.load(self.model_path)
        return self._model

    def predict(self, text: str) -> dict:
        model = self._load()
        probabilities = model.predict_proba([text])[0]
        classes = model.named_steps["classifier"].classes_
        order = np.argsort(probabilities)[::-1]

        top_predictions = [
            {
                "label": str(classes[index]),
                "score": round(float(probabilities[index]), 4),
            }
            for index in order[:3]
        ]

        return {
            "label": top_predictions[0]["label"],
            "confidence": top_predictions[0]["score"],
            "top_predictions": top_predictions,
            "backend": "bitext_tfidf_logistic_regression",
        }