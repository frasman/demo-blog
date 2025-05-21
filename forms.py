from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField, SelectField, TextAreaField
from wtforms.validators import DataRequired, URL, Email, Length
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Titolo (max 50)", validators=[DataRequired(), Length(max=50)])
    subtitle = StringField("Sottotitolo", validators=[DataRequired()])
    cover_image = StringField("URL Immagine di Copertina", validators=[DataRequired(), URL()])
    category = SelectField("Categoria", choices=[("consigli", "Consigli"), ("news", "News"), ("esperienze", "Esperienze")], validators=[DataRequired()])
    body = CKEditorField("Contenuto", validators=[DataRequired()])
    meta_description = StringField("Meta Description (max 160)", validators=[DataRequired(), Length(max=160)])
    meta_keywords = StringField("Meta Keywords (separate da virgole)", validators=[Length(max=255)])
    status = SelectField("Stato", choices=[("draft", "Bozza"), ("published", "Pubblicato")], default="draft")
    submit = SubmitField("Pubblica")


# Create a form to register new users
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


# Create a form to login existing users
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


# Create a form to add comments
class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")

# Create a form to send an email
class ContactForm(FlaskForm):
    name = StringField("Nome", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=100)])
    subject = StringField("Oggetto", validators=[DataRequired(), Length(max=150)])
    message = TextAreaField("Messaggio", validators=[DataRequired(), Length(max=2000)])
    recaptcha = RecaptchaField()
    submit = SubmitField("Invia messaggio")