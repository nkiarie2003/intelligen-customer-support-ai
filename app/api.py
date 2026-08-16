from functools import wraps
from flask import Blueprint, current_app, jsonify, request

from .ai.engine import get_ai_engine
from .ai.provenance import load_training_provenance
from .ai.safety import minimise_sensitive_text
from .extensions import csrf
from .models import KnowledgeDocument

bp = Blueprint("api", __name__, url_prefix="/api/v1")
csrf.exempt(bp)


def api_key_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        expected = current_app.config["API_DEMO_KEY"]
        supplied = request.headers.get("X-API-Key", "")
        if not expected or supplied != expected:
            return jsonify({"error": "unauthorized"}), 401
        return view(*args, **kwargs)
    return wrapped


@bp.get("/health")
def health():
    artifact_dir = current_app.config["ARTIFACT_DIR"]
    return jsonify(
        {
            "status": "ok",
            "service": "customer-intelligence",
            "inference_mode": "local_flask",
            "classifier_ready": (artifact_dir / "complaint_classifier.joblib").exists(),
        }
    )


@bp.get("/model-provenance")
@api_key_required
def model_provenance():
    return jsonify(load_training_provenance(current_app.config["ARTIFACT_DIR"]))


@bp.post("/analyze")
@api_key_required
def analyze():
    payload = request.get_json(silent=True) or {}
    subject = str(payload.get("subject", "Customer support request"))[:160]
    message = str(payload.get("message", "")).strip()
    if len(message) < 15:
        return jsonify({"error": "message must contain at least 15 characters"}), 400

    safe_subject, subject_warnings = minimise_sensitive_text(subject)
    safe_message, message_warnings = minimise_sensitive_text(message)
    docs = [
        {"title": d.title, "content": d.content}
        for d in KnowledgeDocument.query.filter_by(active=True).all()
    ]
    result = get_ai_engine().analyze(safe_subject, safe_message, docs)
    result["privacy_redactions"] = subject_warnings + message_warnings
    return jsonify(result)
