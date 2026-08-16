from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from .extensions import db
from .forms import KnowledgeForm
from .models import AuditLog, KnowledgeDocument, User
from .utils import admin_required, audit

bp = Blueprint("admin", __name__, url_prefix="/admin-tools")


@bp.route("/knowledge", methods=["GET", "POST"])
@login_required
@admin_required
def knowledge():
    form = KnowledgeForm()
    if form.validate_on_submit():
        doc = KnowledgeDocument(
            title=form.title.data.strip(),
            content=form.content.data.strip(),
            active=form.active.data,
        )
        db.session.add(doc)
        db.session.flush()
        audit("knowledge_added", "knowledge_document", doc.id, {"title": doc.title})
        db.session.commit()
        flash("Knowledge document added to the RAG corpus.", "success")
        return redirect(url_for("admin.knowledge"))
    docs = KnowledgeDocument.query.order_by(KnowledgeDocument.created_at.desc()).all()
    return render_template("admin/knowledge.html", form=form, docs=docs)


@bp.route("/knowledge/<int:doc_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_knowledge(doc_id):
    doc = KnowledgeDocument.query.get_or_404(doc_id)
    doc.active = not doc.active
    audit("knowledge_toggled", "knowledge_document", doc.id, {"active": doc.active})
    db.session.commit()
    return redirect(url_for("admin.knowledge"))


@bp.route("/users")
@login_required
@admin_required
def users():
    return render_template("admin/users.html", users=User.query.order_by(User.created_at.desc()).all())


@bp.route("/audit")
@login_required
@admin_required
def audit_log():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(200).all()
    return render_template("admin/audit.html", logs=logs)
