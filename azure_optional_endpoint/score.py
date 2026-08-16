import json
import os
from pathlib import Path
import joblib

model = None


def init():
    global model
    model_dir = Path(os.environ.get("AZUREML_MODEL_DIR", "."))
    candidates = list(model_dir.rglob("complaint_classifier.joblib"))
    if not candidates:
        raise FileNotFoundError("complaint_classifier.joblib not found under AZUREML_MODEL_DIR")
    model = joblib.load(candidates[0])


def run(raw_data):
    try:
        data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
        text = str(data.get("text", ""))
        if not text:
            return {"error": "text is required"}
        probs = model.predict_proba([text])[0]
        classes = model.named_steps["classifier"].classes_
        order = probs.argsort()[::-1]
        top = [
            {"label": str(classes[i]), "score": round(float(probs[i]), 4)}
            for i in order[:3]
        ]
        return {
            "label": top[0]["label"],
            "confidence": top[0]["score"],
            "top_predictions": top,
            "backend": "azure_ml_tfidf_logistic_regression",
        }
    except Exception as exc:
        return {"error": str(exc)}
