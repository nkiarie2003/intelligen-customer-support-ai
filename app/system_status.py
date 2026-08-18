import json
from flask import Blueprint, current_app, render_template
from flask_login import login_required

from .ai.provenance import load_training_provenance
from .utils import admin_required

bp = Blueprint("system_status", __name__, url_prefix="/system")


@bp.route("/status")
@login_required
@admin_required
def status():
    artifacts = current_app.config["ARTIFACT_DIR"]
    metrics_path = artifacts / "metrics.json"
    metrics = None
    if metrics_path.exists():
        try:
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        except Exception:
            metrics = None

    components = [
        {
            "name": "Supervised complaint classifier",
            "enabled": (artifacts / "complaint_classifier.joblib").exists(),
            "detail": "TF-IDF + Logistic Regression; live inference runs in Flask.",
        },
        {
            "name": "VADER sentiment",
            "enabled": True,
            "detail": "Lexicon-based baseline sentiment analysis.",
        },
        {
            "name": "Zero-shot transformer",
            "enabled": current_app.config["ENABLE_ZERO_SHOT"],
            "detail": current_app.config["ZERO_SHOT_MODEL"],
        },
        {
            "name": "Transformer sentiment",
            "enabled": current_app.config["ENABLE_TRANSFORMER_SENTIMENT"],
            "detail": current_app.config["SENTIMENT_MODEL"],
        },
        {
            "name": "Semantic RAG embeddings",
            "enabled": current_app.config["ENABLE_EMBEDDINGS"],
            "detail": current_app.config["EMBEDDING_MODEL"],
        },
        {
            "name": "Local generative model",
            "enabled": current_app.config["ENABLE_LOCAL_GENERATOR"],
            "detail": current_app.config["GENERATOR_MODEL"],
        },
        {
            "name": "Twitter conversation retrieval",
            "enabled": current_app.config["ENABLE_CONVERSATION_EXAMPLES"],
            "detail": "Historical replies are style examples only; policy RAG remains authoritative.",
        },
    ]

    return render_template(
        "system/status.html",
        components=components,
        metrics=metrics,
        provenance=load_training_provenance(artifacts),
        inference_mode=current_app.config["INFERENCE_MODE"],
    )
