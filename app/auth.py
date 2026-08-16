from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from .extensions import db
from .forms import LoginForm, RegisterForm
from .models import User
from .utils import audit

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        if User.query.filter_by(username=username).first():
            flash("That username is already in use.", "error")
            return render_template("auth/register.html", form=form)
        user = User(username=username, role="customer")
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()
        audit("register", "user", user.id, {"role": "customer"})
        db.session.commit()
        login_user(user)
        flash("Customer account created.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Signed in.", "success")
            return redirect(url_for("main.dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("auth/login.html", form=form)


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Signed out.", "success")
    return redirect(url_for("main.index"))
