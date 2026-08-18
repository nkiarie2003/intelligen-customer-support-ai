from datetime import datetime, timezone
from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from .ai.engine import get_ai_engine
from .ai.safety import minimise_sensitive_text
from .extensions import db
from .forms import ComplaintForm, ReviewForm
from .models import Complaint, KnowledgeDocument
from .utils import admin_required, audit, staff_required

bp = Blueprint("complaints", __name__, url_prefix="/complaints")


def _can_view(complaint):
    return current_user.is_staff or complaint.user_id == current_user.id


def _active_docs():
    return [
        {"title": d.title, "content": d.content}
        for d in KnowledgeDocument.query.filter_by(active=True).all()
    ]


def _apply_analysis(complaint: Complaint, result: dict) -> None:
    complaint.ai_category = result["category"]["label"]
    complaint.ai_category_confidence = result["category"].get("confidence")
    complaint.ai_sentiment = result["sentiment"]["label"]
    complaint.ai_sentiment_score = result["sentiment"].get("score")
    complaint.ai_priority = result["priority"]["label"]
    complaint.ai_priority_score = result["priority"]["score"]
    complaint.ai_explanation = result["explanation"]
    complaint.ai_retrieval = result["retrieval"]
    complaint.ai_reply = result["suggested_reply"]["text"]
    complaint.ai_backends = result["backends"]


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    form = ComplaintForm()
    if form.validate_on_submit():
        subject, subject_warnings = minimise_sensitive_text(form.subject.data.strip())
        message, message_warnings = minimise_sensitive_text(form.message.data.strip())
        privacy_warnings = subject_warnings + message_warnings

        result = get_ai_engine().analyze(subject, message, _active_docs())
        result["explanation"]["privacy_minimisation"] = privacy_warnings

        complaint = Complaint(user_id=current_user.id, subject=subject, message=message)
        _apply_analysis(complaint, result)
        db.session.add(complaint)
        db.session.flush()
        audit(
            "complaint_created_and_analyzed",
            "complaint",
            complaint.public_id,
            {
                "category": complaint.ai_category,
                "priority": complaint.ai_priority,
                "privacy_redactions": privacy_warnings,
            },
        )
        db.session.commit()
        if privacy_warnings:
            flash(
                "Complaint submitted. Potentially sensitive values were removed before the complaint was stored.",
                "success",
            )
        else:
            flash("Complaint submitted. A support team member will review it and an approved response will appear in your case.", "success")
        return redirect(url_for("complaints.detail", public_id=complaint.public_id))
    return render_template("complaints/new.html", form=form)


@bp.route("/<public_id>")
@login_required
def detail(public_id):
    complaint = Complaint.query.filter_by(public_id=public_id).first_or_404()
    if not _can_view(complaint):
        abort(403)
    form = ReviewForm(edited_reply=complaint.human_reply or complaint.ai_reply)
    return render_template("complaints/detail.html", complaint=complaint, form=form)


@bp.route("/<public_id>/reanalyze", methods=["POST"])
@login_required
@admin_required
def reanalyze(public_id):
    complaint = Complaint.query.filter_by(public_id=public_id).first_or_404()
    result = get_ai_engine().analyze(complaint.subject, complaint.message, _active_docs())
    _apply_analysis(complaint, result)
    complaint.reply_status = "pending"
    complaint.human_reply = None
    complaint.reviewed_at = None
    audit(
        "complaint_reanalyzed",
        "complaint",
        complaint.public_id,
        {"category": complaint.ai_category, "priority": complaint.ai_priority},
    )
    db.session.commit()
    flash("Complaint re-analysed using the currently loaded model and AI configuration.", "success")
    return redirect(url_for("complaints.detail", public_id=public_id))


@bp.route("/<public_id>/approve", methods=["POST"])
@login_required
@staff_required
def approve(public_id):
    complaint = Complaint.query.filter_by(public_id=public_id).first_or_404()
    form = ReviewForm()
    if form.validate_on_submit():
        reviewed, warnings = minimise_sensitive_text(form.edited_reply.data.strip())
        complaint.human_reply = reviewed
        complaint.reply_status = "approved"
        complaint.status = "reviewed"
        complaint.assigned_to_id = current_user.id
        complaint.reviewed_at = datetime.now(timezone.utc)
        audit(
            "ai_reply_approved",
            "complaint",
            complaint.public_id,
            {"privacy_redactions": warnings},
        )
        db.session.commit()
        flash("Response approved by a human reviewer.", "success")
    else:
        flash("Please provide a valid reviewed response.", "error")
    return redirect(url_for("complaints.detail", public_id=public_id))


@bp.route("/<public_id>/reject", methods=["POST"])
@login_required
@staff_required
def reject(public_id):
    complaint = Complaint.query.filter_by(public_id=public_id).first_or_404()
    complaint.reply_status = "rejected"
    complaint.assigned_to_id = current_user.id
    complaint.reviewed_at = datetime.now(timezone.utc)
    audit("ai_reply_rejected", "complaint", complaint.public_id)
    db.session.commit()
    flash("AI draft rejected. No automated response has been sent.", "success")
    return redirect(url_for("complaints.detail", public_id=public_id))


@bp.route("/<public_id>/close", methods=["POST"])
@login_required
@staff_required
def close(public_id):
    complaint = Complaint.query.filter_by(public_id=public_id).first_or_404()
    complaint.status = "closed"
    audit("complaint_closed", "complaint", complaint.public_id)
    db.session.commit()
    flash("Complaint closed.", "success")
    return redirect(url_for("complaints.detail", public_id=public_id))
