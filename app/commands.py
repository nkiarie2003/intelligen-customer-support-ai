from datetime import datetime, timedelta, timezone
import click
from flask import current_app
from flask.cli import with_appcontext

from .ai.training import train_classifier
from .extensions import db
from .models import Complaint, User


@click.command("train-models")
@with_appcontext
def train_models_command():
    metrics = train_classifier(
        current_app.config["TRAINING_DATA"], current_app.config["ARTIFACT_DIR"]
    )
    click.echo(
        f"Classifier trained. Accuracy={metrics['accuracy']}, "
        f"precision={metrics['macro_precision']}, recall={metrics['macro_recall']}, "
        f"macro-F1={metrics['macro_f1']}"
    )


@click.command("create-admin")
@click.argument("username")
@click.option("--role", type=click.Choice(["agent", "admin"]), default="admin")
@click.password_option()
@with_appcontext
def create_admin_command(username, role, password):
    if User.query.filter_by(username=username).first():
        raise click.ClickException("Username already exists.")
    user = User(username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f"Created {role}: {username}")


@click.command("purge-old-closed")
@click.option("--days", type=int, default=None, help="Delete closed complaints older than this many days.")
@click.option("--yes", is_flag=True, help="Required acknowledgement for destructive deletion.")
@with_appcontext
def purge_old_closed_command(days, yes):
    if not yes:
        raise click.ClickException("Add --yes to confirm deletion.")
    days = days or current_app.config["DATA_RETENTION_DAYS"]
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    records = Complaint.query.filter(Complaint.status == "closed", Complaint.updated_at < cutoff).all()
    count = len(records)
    for record in records:
        db.session.delete(record)
    db.session.commit()
    click.echo(f"Deleted {count} closed complaint(s) older than {days} days.")
