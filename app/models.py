from datetime import datetime, timezone
import uuid

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="customer", index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    complaints = db.relationship("Complaint", back_populates="customer", foreign_keys="Complaint.user_id")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_staff(self) -> bool:
        return self.role in {"agent", "admin"}


class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    subject = db.Column(db.String(160), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="open", index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    ai_category = db.Column(db.String(80), nullable=True)
    ai_category_confidence = db.Column(db.Float, nullable=True)
    ai_sentiment = db.Column(db.String(30), nullable=True)
    ai_sentiment_score = db.Column(db.Float, nullable=True)
    ai_priority = db.Column(db.String(20), nullable=True)
    ai_priority_score = db.Column(db.Integer, nullable=True)
    ai_explanation = db.Column(db.JSON, nullable=True)
    ai_retrieval = db.Column(db.JSON, nullable=True)
    ai_reply = db.Column(db.Text, nullable=True)
    ai_backends = db.Column(db.JSON, nullable=True)

    human_reply = db.Column(db.Text, nullable=True)
    reply_status = db.Column(db.String(20), nullable=False, default="pending")
    reviewed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    customer = db.relationship("User", foreign_keys=[user_id], back_populates="complaints")
    assigned_to = db.relationship("User", foreign_keys=[assigned_to_id])


class KnowledgeDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    content = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    action = db.Column(db.String(80), nullable=False)
    entity_type = db.Column(db.String(60), nullable=False)
    entity_id = db.Column(db.String(80), nullable=True)
    detail = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    actor = db.relationship("User")
