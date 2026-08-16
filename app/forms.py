from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    confirm = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Create customer account")


class ComplaintForm(FlaskForm):
    subject = StringField("Subject", validators=[DataRequired(), Length(min=4, max=160)])
    message = TextAreaField("Complaint or support message", validators=[DataRequired(), Length(min=15, max=5000)])
    submit = SubmitField("Analyse and submit")


class ReviewForm(FlaskForm):
    edited_reply = TextAreaField("Human-reviewed response", validators=[DataRequired(), Length(min=5, max=5000)])
    submit = SubmitField("Approve response")


class KnowledgeForm(FlaskForm):
    title = StringField("Policy title", validators=[DataRequired(), Length(min=3, max=180)])
    content = TextAreaField("Policy content", validators=[DataRequired(), Length(min=20, max=12000)])
    active = BooleanField("Active", default=True)
    submit = SubmitField("Add knowledge document")
