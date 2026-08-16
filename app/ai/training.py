from pathlib import Path
from datetime import datetime, timezone
import json
import os
import platform

import joblib
import pandas as pd
import sklearn
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


def _provenance(data_path: Path, metrics: dict) -> dict:
    return {
        "training_platform": os.getenv("TRAINING_PLATFORM", "local"),
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "hostname": platform.node(),
        "operating_system": platform.platform(),
        "python_version": platform.python_version(),
        "scikit_learn_version": sklearn.__version__,
        "dataset_path": str(data_path),
        "dataset_rows": metrics["dataset_rows"],
        "classes": metrics["classes"],
        "azure": {
            "subscription": os.getenv("AZURE_ML_SUBSCRIPTION", ""),
            "resource_group": os.getenv("AZURE_ML_RESOURCE_GROUP", ""),
            "workspace": os.getenv("AZURE_ML_WORKSPACE", ""),
            "compute": os.getenv("AZURE_ML_COMPUTE", ""),
        },
        "architecture": "cloud-training/local-inference",
        "note": (
            "When training_platform is azure_ml_compute_instance, the script was run "
            "interactively on an existing Azure ML compute instance. Flask inference remains local."
        ),
    }


def train_classifier(data_path: Path, artifact_dir: Path) -> dict:
    data_path = Path(data_path)
    if not data_path.exists():
        raise FileNotFoundError(
            f"Processed training data not found: {data_path}. "
            "Download the Kaggle datasets and run: python scripts/prepare_datasets.py"
        )
    artifact_dir = Path(artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(data_path).dropna(subset=["message", "category"])
    df["message"] = df["message"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip()
    df = df[(df["message"].str.len() >= 20) & df["category"].ne("")]

    counts = df["category"].value_counts()
    valid_classes = counts[counts >= 5].index
    df = df[df["category"].isin(valid_classes)].copy()
    if df["category"].nunique() < 2:
        raise ValueError("At least two complaint categories with five or more rows are required.")

    X_train, X_test, y_train, y_test = train_test_split(
        df["message"],
        df["category"],
        test_size=0.20,
        random_state=42,
        stratify=df["category"],
    )

    pipeline = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    stop_words="english",
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.98,
                    max_features=60000,
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
    pipeline.fit(X_train, y_train)
    pred = pipeline.predict(X_test)
    classes = list(pipeline.named_steps["classifier"].classes_)

    metrics = {
        "dataset": "CFPB Consumer Complaint Database (Kaggle mirror; processed real data)",
        "dataset_rows": int(len(df)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "accuracy": round(float(accuracy_score(y_test, pred)), 4),
        "macro_precision": round(float(precision_score(y_test, pred, average="macro", zero_division=0)), 4),
        "macro_recall": round(float(recall_score(y_test, pred, average="macro", zero_division=0)), 4),
        "macro_f1": round(float(f1_score(y_test, pred, average="macro")), 4),
        "weighted_f1": round(float(f1_score(y_test, pred, average="weighted")), 4),
        "classes": classes,
        "class_distribution": {
            str(k): int(v) for k, v in df["category"].value_counts().sort_index().items()
        },
        "classification_report": classification_report(y_test, pred, output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(y_test, pred, labels=classes).tolist(),
        "evaluation_design": {
            "split": "stratified 80/20 hold-out",
            "random_state": 42,
            "model": "TF-IDF (1-2 grams) + balanced multinomial Logistic Regression",
        },
        "note": (
            "Prototype evaluation on a processed sample of real CFPB complaint narratives. "
            "Kaggle/CFPB source limitations, category mapping, class imbalance and domain shift "
            "must be discussed before production use."
        ),
    }

    joblib.dump(pipeline, artifact_dir / "complaint_classifier.joblib")
    (artifact_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    provenance = _provenance(data_path, metrics)
    (artifact_dir / "training_provenance.json").write_text(
        json.dumps(provenance, indent=2), encoding="utf-8"
    )
    return metrics
