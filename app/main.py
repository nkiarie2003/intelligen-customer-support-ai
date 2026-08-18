import json
from collections import Counter
from flask import Blueprint, current_app, render_template, request
from flask_login import current_user, login_required

from .models import Complaint
from .utils import admin_required

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/dashboard")
@login_required
def dashboard():
    query = Complaint.query
    if not current_user.is_staff:
        query = query.filter_by(user_id=current_user.id)
    all_complaints = query.order_by(Complaint.created_at.desc()).all()

    q = (request.args.get("q") or "").strip().lower()
    status_filter = (request.args.get("status") or "all").strip().lower()
    complaints = all_complaints
    if q:
        complaints = [
            c for c in complaints
            if q in c.subject.lower()
            or q in c.public_id.lower()
            or (c.customer and q in c.customer.username.lower())
        ]
    if status_filter != "all":
        if status_filter == "response_available":
            complaints = [c for c in complaints if c.reply_status == "approved"]
        elif status_filter == "awaiting_review":
            complaints = [c for c in complaints if c.reply_status in {"pending", "rejected"} and c.status != "closed"]
        else:
            complaints = [c for c in complaints if c.status == status_filter]

    counts = {
        "total": len(all_complaints),
        "open": sum(c.status == "open" for c in all_complaints),
        "closed": sum(c.status == "closed" for c in all_complaints),
        "pending": sum(c.reply_status in {"pending", "rejected"} and c.status != "closed" for c in all_complaints),
        "responses": sum(c.reply_status == "approved" for c in all_complaints),
        "high": sum(c.ai_priority in {"high", "critical"} for c in all_complaints),
    }
    return render_template(
        "dashboard.html",
        complaints=complaints,
        counts=counts,
        filters={"q": q, "status": status_filter},
    )


@bp.route("/analytics")
@login_required
@admin_required
def analytics():
    complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()
    total = max(len(complaints), 1)

    def dist(attr):
        counts = Counter((getattr(c, attr) or "unknown") for c in complaints)
        return [
            {
                "label": label.replace("_", " ").title(),
                "count": count,
                "pct": round(count * 100 / total, 1),
            }
            for label, count in counts.most_common()
        ]

    stats = {
        "total": len(complaints),
        "approved": sum(c.reply_status == "approved" for c in complaints),
        "closed": sum(c.status == "closed" for c in complaints),
        "critical": sum(c.ai_priority == "critical" for c in complaints),
    }
    return render_template(
        "analytics.html",
        stats=stats,
        categories=dist("ai_category"),
        sentiments=dist("ai_sentiment"),
        priorities=dist("ai_priority"),
    )


@bp.route("/model-metrics")
@login_required
@admin_required
def model_metrics():
    path = current_app.config["ARTIFACT_DIR"] / "metrics.json"
    metrics = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
    return render_template("metrics.html", metrics=metrics)
