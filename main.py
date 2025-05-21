import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash, abort, request, Response
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_bootstrap import Bootstrap5
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_mail import Mail, Message
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.sql.expression import func
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from forms import LoginForm, RegisterForm, CreatePostForm, CommentForm, ContactForm
from slugify import slugify
import cloudinary.uploader
import pytz


load_dotenv(".env")

app = Flask(__name__)
SECRET_KEY = os.getenv("FLASK_KEY")
app.config["SECRET_KEY"] = SECRET_KEY

ckeditor = CKEditor(app)

Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)



cloudinary.config(
    cloud_name = os.getenv("CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_KEY"),
    api_secret = os.getenv("CLOUDINARY_SECRET_KEY"),
    secure = True
)

def is_maintenance_mode():
    return os.getenv("MAINTENANCE_MODE", "false").lower() == "true"

app.config['MAIL_SERVER'] = 'smtp.ionos.it'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_USER')

mail = Mail(app)


app.config['RECAPTCHA_PUBLIC_KEY'] = os.getenv("RECAPTCHA_PUBLIC_KEY")
app.config['RECAPTCHA_PRIVATE_KEY'] = os.getenv("RECAPTCHA_PRIVATE_KEY")

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

def maintenance_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if is_maintenance_mode():
            return render_template('maintenance.html'), 503
        return f(*args, **kwargs)
    return decorated_function

gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


#CREATE DATABASE
class Base(DeclarativeBase):
    pass

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///posts.db")


db = SQLAlchemy(model_class=Base)
db.init_app(app)

migrate = Migrate(app, db)

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('users.id'))
    author = relationship("User", back_populates="posts")
    title: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    cover_image: Mapped[str] = mapped_column(String(500), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    meta_description: Mapped[str] = mapped_column(String(160), nullable=True)
    meta_keywords = db.Column(db.String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(10), default="draft")

    comments = relationship("Comment", back_populates="parent_post")



class User(UserMixin, db.Model):
    __tablename__ = "users"
    id : Mapped[int] = mapped_column(Integer, primary_key = True)
    email : Mapped[str] = mapped_column(String(100), unique = True)
    password : Mapped[str] = mapped_column(String(100))
    name : Mapped[str] = mapped_column(String(100))

    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")

class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    post_id: Mapped[str] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

with app.app_context():
    db.create_all()

year = datetime.now().strftime("%m/%y")


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

def convert_to_rome_time(utc_time):
    if utc_time.tzinfo is None:
        utc_time = pytz.utc.localize(utc_time)
    rome_tz = pytz.timezone('Europe/Rome')
    return utc_time.astimezone(rome_tz)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Devi effettuare il login per accedere a questa pagina.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
@maintenance_required
def home():
    latest_posts = db.session.execute(
        db.select(BlogPost).where(BlogPost.status == "published").order_by(BlogPost.date.desc()).limit(4)
    ).scalars().all()


    random_posts = db.session.execute(
        db.select(BlogPost).where(BlogPost.status == "published").order_by(func.random()).limit(6)
    ).scalars().all()


    return render_template(
        "index.html",
        latest_posts=latest_posts,
        random_posts=random_posts,
        current_user=current_user
    )

@app.route("/about_us")
@maintenance_required
def about():
    return render_template("about.html")

@app.route("/advices")
@maintenance_required
def advices():
    categorized_post = db.session.execute(
        db.select(BlogPost).where(BlogPost.category == "consigli").order_by(BlogPost.date.desc()).limit(4)
    ).scalars().all()
    return render_template("advices.html",
                           categorized_post = categorized_post)

@app.route("/contact", methods=["GET", "POST"])
@maintenance_required
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        subject = form.subject.data
        message_body = form.message.data

        full_message = f"Da: {name} <{email}>\n\n{message_body}"

        msg = Message(subject=subject,
                      body=full_message,
                      recipients=["info@twoontheroad.it"])
        try:
            mail.send(msg)
            flash("Messaggio inviato con successo!", "success")
        except Exception as e:
            flash(f"Errore durante l'invio: {e}", "danger")
        return redirect(url_for("contact"))
    return render_template("contact.html", form=form)

@app.route("/disclaimer")
@maintenance_required
def disclaimer():
    return render_template("disclaimer.html", CURRENT_MONTH = year )

@app.route("/privacy_policy")
@maintenance_required
def privacy_policy():
    return render_template("privacy.html")

@app.route("/blog")
@maintenance_required
def blog():
    per_page = 8
    page = request.args.get('page', 1, type=int)

    posts_query = db.session.query(BlogPost).filter(BlogPost.status == "published").order_by(BlogPost.date.desc())
    posts_paginated = posts_query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template("blog.html", all_posts=posts_paginated.items, pagination=posts_paginated, current_user=current_user)

@app.route("/post/<string:slug>", methods=["GET", "POST"])
@maintenance_required
def show_post(slug):
    post = db.session.execute(db.select(BlogPost).where(BlogPost.slug==slug)).scalar()

    requested_post = post
    requested_post.date = convert_to_rome_time(requested_post.date)

    comment_form = CommentForm()

    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Devi effettuare il login o registrarti per commentare.")
            return redirect(url_for("login"))


        new_comment = Comment(
            text=comment_form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post,
            date=datetime.now(timezone.utc)
        )
        db.session.add(new_comment)
        db.session.commit()
        flash("Il tuo commento è stato aggiunto!", "success")

        comment_form.comment_text.data = ""

    for comment in requested_post.comments:
        comment.date = convert_to_rome_time(comment.date)

    return render_template("post.html", post=requested_post, current_user=current_user, form=comment_form)


@app.route("/register", methods = ["GET", "POST"])
@maintenance_required
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        # Check if user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("Questa mail è già registrata, fai il login!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("home"))
    return render_template("register.html", form=form, current_user=current_user)


@app.route("/login", methods = ["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if not user:
            flash("Questa mail non esiste, prova di nuovo")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password sbagliata, prova di nuovo')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('blog'))
    return render_template("login.html", form = form, current_user = current_user )

@app.route("/logout")
@maintenance_required
def logout():
    logout_user()
    flash("Sei stato disconnesso con successo.", "info")
    return redirect(url_for("home"))

@app.route("/new-post", methods=["GET", "POST"])
@maintenance_required
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():

        generate_slug = slugify(form.title.data)
        existing_slug = db.session.execute(db.select(BlogPost).where(BlogPost.slug == generate_slug)).scalar()
        if existing_slug:
            generate_slug = generate_slug + "-" + str(datetime.now(timezone.utc).timestamp())

        status = form.status.data if form.status.data else "draft"

        new_post = BlogPost(
            title=form.title.data,
            slug=generate_slug,
            subtitle=form.subtitle.data,
            cover_image=form.cover_image.data,
            category = form.category.data,
            body=form.body.data,
            meta_description=form.meta_description.data,
            meta_keywords = form.meta_keywords.data,
            author=current_user,
            date=datetime.now(timezone.utc),
            status = status,
        )

        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("blog"))

    return render_template("make-post.html", form=form, current_user=current_user)

@app.route("/edit-post/<string:slug>", methods=["GET", "POST"])
@maintenance_required
@admin_only
def edit_post(slug):
    post = db.session.execute(db.select(BlogPost).where(BlogPost.slug == slug)).scalar()
    requested_post = post.slug
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        cover_image=post.cover_image,
        author=post.author,
        body=post.body,
        category=post.category,
        status=post.status,
        meta_description=post.meta_description,
        meta_keywords= post.meta_keywords,
    )
    if edit_form.validate_on_submit():
        prev_status = post.status
        new_status = edit_form.status.data

        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.cover_image = edit_form.cover_image.data
        post.author = current_user
        post.body = edit_form.body.data
        post.category = edit_form.category.data
        post.meta_description = edit_form.meta_description.data
        post.meta_keywords = edit_form.meta_keywords.data

        # Controlla se lo stato passa da "draft" a "published"
        if prev_status == "draft" and new_status == "published":
            post.date = datetime.now(timezone.utc)
        post.status = new_status

        db.session.add(post)
        db.session.commit()

        post_in_db = db.session.execute(db.select(BlogPost).where(BlogPost.slug == slug)).scalar()
        return redirect(url_for("show_post", slug=requested_post))
    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)

@app.route("/delete-post/<string:slug>", methods=["GET", "POST"])
@admin_only
def delete_post(slug):
    post_to_delete = db.session.execute(db.select(BlogPost).where(BlogPost.slug == slug)).scalar()

    if post_to_delete:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Il post è stato eliminato con successo.", "success")
    else:
        flash("Post non trovato.", "danger")

    return redirect(url_for("blog"))

@app.route("/delete-comment/<int:comment_id>", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = db.session.get(Comment, comment_id)
    if not comment:
        flash("Commento non trovato.", "danger")
        return redirect(request.referrer or url_for("home"))

    if comment.author_id != current_user.id and current_user.id != 1:
        flash("Non hai il permesso per eliminare questo commento.", "danger")
        return redirect(request.referrer or url_for("home"))

    db.session.delete(comment)
    db.session.commit()
    flash("Commento eliminato con successo.", "success")
    return redirect(request.referrer or url_for("home"))


@app.route("/admin/toggle-maintenance")
@admin_only
def toggle_maintenance():
    current_mode = is_maintenance_mode()
    new_mode = "false" if current_mode else "true"

    lines = []
    with open(".env", "r") as file:
        for line in file:
            if line.startswith("MAINTENANCE_MODE"):
                lines.append(f"MAINTENANCE_MODE={new_mode}\n")
            else:
                lines.append(line)

    with open(".env", "w") as file:
        file.writelines(lines)

    load_dotenv(override=True)

    message = "Modalità manutenzione attivata" if new_mode == "true" else "Modalità manutenzione disattivata"
    flash(message, "info")

    return redirect(url_for("home"))

@app.route('/bozze')
def bozze():
    bozze_posts = db.session.query(BlogPost).filter(BlogPost.status == "draft").order_by(BlogPost.date.desc())
    return render_template('bozze.html', bozze=bozze_posts)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.route("/sitemap.xml")
def sitemap():
    pages = [
        "/", "/about_us", "/advices", "/contact", "/disclaimer", "/privacy_policy", "/blog"
    ]

    posts = db.session.execute(db.select(BlogPost).where(BlogPost.status == "published")).scalars().all()
    for post in posts:
        pages.append(f"/post/{post.slug}")

    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>'
    sitemap_xml += "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"

    for page in pages:
        sitemap_xml += f"""
        <url>
            <loc>{request.url_root[:-1]}{page}</loc>
            <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
            <changefreq>daily</changefreq>
            <priority>0.8</priority>
        </url>
        """

    sitemap_xml += "</urlset>"

    return Response(sitemap_xml, mimetype="application/xml")

@app.route("/robots.txt")
def robots_txt():
    return Response(
        "User-agent: *\n"
        "Disallow: /admin\n"
        "Disallow: /login\n"
        "Disallow: /register\n"
        "Sitemap: https://www.twoontheroad.it/sitemap.xml\n",
        mimetype="text/plain"
    )

if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=5000, debug = True)
    pass

