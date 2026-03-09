from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from src.api.forms.agencie_form import AgencieSignupForm
from src.api.forms.auth_form import (
    ChangeEmailForm,
    LoginForm,
    PasswordResetForm,
    PasswordResetRequestForm,
)
from src.api.forms.owner_form import OwnerHouseSignupForm
from src.infrastructure.config.plugins import db, login_manager, oauth
from src.infrastructure.external.email import send_email
from src.infrastructure.persistence.models import User
from src.infrastructure.security import utils

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth/")


@login_manager.unauthorized_handler
def unauthorized():
    flash("Vous devez être connecté pour voir cette page.")
    return redirect(url_for("auth_bp.login"))


@auth_bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        # User model from persistence has ping if it inherits from proper mixin
        # In this project, DefaultUserInfoModel might have it or ping is in TimestampMixin?
        # Let's check the mixin if needed, but assuming it exists for now
        if hasattr(current_user, "ping"):
            current_user.ping()


@auth_bp.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.is_administrator():
            return redirect(url_for("admin_bp.dashboard"))
        return redirect(url_for("owner_bp.dashboard"))

    form = LoginForm(request.form)
    if form.validate_on_submit():
        email_or_phone = form.email_or_phone.data
        # Note: find_by_email_and_phone might need to be moved to a repository or kept in Model
        # Since we kept it in Model for now (looking at models.py creation), should work
        user = User.query.filter(
            (User.vn_addr_email == email_or_phone)
            | (User.vn_phonenumber_one == email_or_phone)
        ).first()

        if user and user.vn_activated and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next_page = request.args.get("next")
            if next_page is None or not next_page.startswith("/"):
                if user.is_administrator():
                    next_page = url_for("admin_bp.dashboard")
                else:
                    next_page = url_for("owner_bp.dashboard")
            flash(
                f"Hello, bienvenue sur votre tableau de bord: {user.vn_fullname!r}",
                category="success",
            )
            return redirect(next_page)
        else:
            error_message = "Identifiants invalides ou compte désactivé."
            if user and not user.vn_activated:
                error_message = "Votre compte a été désactivé ! Veuillez contacter l'administrateur système."

            flash(error_message, category="danger")

    page_title = "Se connecter"
    return render_template("auth/login.html", page_title=page_title, form=form)


@auth_bp.route("/owner/signup/", methods=["GET", "POST"])
def registerowner_page():
    if current_user.is_authenticated and current_user.vn_activated:
        flash("Vous êtes déjà inscrit(e).", category="info")
        return redirect(url_for("owner_bp.dashboard"))

    form = OwnerHouseSignupForm()
    if form.validate_on_submit():
        user_to_create = User(
            vn_gender=form.gender.data,
            vn_fullname=form.fullname.data,
            vn_addr_email=form.addr_email.data.lower(),
            vn_phonenumber_one=form.phonenumber_one.data,
            vn_cni_number=form.cni_number.data,
            vn_country=form.country.data,
        )
        user_to_create.set_password(form.password.data)
        user_to_create.vn_activated = True
        user_to_create.vn_house_owner = True

        db.session.add(user_to_create)
        db.session.commit()

        msg_success = (
            f"Hey {user_to_create.vn_fullname}, votre compte a été créé ! "
            f"Connectez-vous maintenant !"
        )
        flash(msg_success, category="success")
        return redirect(url_for("auth_bp.login"))

    page_title = "Créer un compte particulier"
    return render_template("auth/signup/owner.html", form=form, page_title=page_title)


@auth_bp.route("/company/signup/", methods=["GET", "POST"])
def agencieregister_page():
    if current_user.is_authenticated and current_user.vn_activated:
        flash("Vous êtes déjà inscrit(e).", category="info")
        return redirect(url_for("owner_bp.dashboard"))

    form = AgencieSignupForm(request.form)
    if form.validate_on_submit():
        user_to_create = User(
            vn_gender=form.gender.data,
            vn_fullname=form.fullname.data,
            vn_addr_email=form.addr_email.data,
            vn_phonenumber_one=form.phonenumber_one.data,
            vn_business_number=form.business_number.data,
            vn_agencie_name=form.agencie_name.data,
            vn_country=form.country.data,
        )
        user_to_create.set_password(form.password.data)
        user_to_create.vn_activated = True
        user_to_create.vn_company = True

        db.session.add(user_to_create)
        db.session.commit()

        msg_success = (
            f"Hey {user_to_create.vn_fullname}, votre compte a été créé ! "
            f"Connectez-vous maintenant !"
        )
        flash(msg_success, category="success")
        return redirect(url_for("auth_bp.login"))

    page_title = "Créer un compte entreprise"
    return render_template("auth/signup/agencie.html", form=form, page_title=page_title)


@auth_bp.route("/reset-password/", methods=["GET", "POST"])
def password_reset_request():
    form = PasswordResetRequestForm(request.form)
    if form.validate_on_submit():
        email = form.addr_email.data.lower()
        user = User.query.filter_by(vn_addr_email=email).first()
        if user:
            token = utils.generate_confirm_token(email)
            send_email(
                user.vn_addr_email,
                "Réinitialiser votre mot de passe",
                "auth/email/reset_password",
                user=user,
                token=token,
            )
            flash(
                "Nous venons de vous envoyer un e-mail avec un lien pour réinitialiser votre mot de passe !",
                category="info",
            )
            return redirect(url_for("auth_bp.login"))
        else:
            flash(
                f"L'adresse e-mail '{email}' n'est pas enregistrée !",
                category="danger",
            )
            return redirect(url_for("auth_bp.password_reset_request"))

    page_title = "Réinitialiser votre mot de passe"
    return render_template("auth/reset_password.html", page_title=page_title, form=form)


@auth_bp.route("/reset-password-confirm/<token>/", methods=["GET", "POST"])
def password_reset(token):
    try:
        email = utils.confirm_token(token)
    except Exception:
        flash(
            "Le lien de réinitialisation de mot de passe est invalide ou expiré.",
            "error",
        )
        return redirect(url_for("auth_bp.login"))

    user = User.query.filter_by(vn_addr_email=email).first()
    if not user:
        flash(
            "Le lien de réinitialisation de mot de passe est invalide ou expiré.",
            "error",
        )
        return redirect(url_for("auth_bp.login"))

    form = PasswordResetForm(request.form)
    if form.validate_on_submit():
        if form.new_password.data != form.confirm_password.data:
            flash("Les mots de passe ne correspondent pas.", "error")
            return redirect(url_for("auth_bp.password_reset", token=token))
        else:
            user.set_password(form.new_password.data)
            db.session.commit()
            flash(
                "Votre mot de passe a été réinitialisé avec succès. Vous pouvez maintenant vous connecter.",
                category="success",
            )
            return redirect(url_for("auth_bp.login"))

    page_title = "Réinitialiser votre mot de passe"
    return render_template(
        "auth/change_password.html", page_title=page_title, form=form, token=token
    )


@auth_bp.route("/change-email/", methods=["GET", "POST"])
@login_required
def change_email_request():
    form = ChangeEmailForm(request.form)
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.addr_email.data.lower()
            token = utils.generate_confirm_token(new_email)
            send_email(
                new_email,
                "Confirmez votre adresse électronique",
                "auth/email/change_email",
                user=current_user,
                token=token,
            )
            flash(
                "Un courriel contenant des instructions pour confirmer votre nouvelle adresse électronique vous a été envoyé.",
                category="info",
            )
            next_url = request.args.get("next") or url_for("owner_bp.dashboard")
            return redirect(next_url)
        else:
            flash("Mot de passe non valide.", category="danger")

    page_title = "Confirmez votre adresse électronique"
    return render_template("auth/change_email.html", page_title=page_title, form=form)


@auth_bp.get("/change-email/<token>/")
@login_required
def change_email(token):
    try:
        email = utils.confirm_token(token)
        if email:
            current_user.vn_addr_email = email
            db.session.commit()
            flash("Votre adresse e-mail a été mise à jour.", category="info")
        else:
            flash("Demande invalide.", category="danger")
    except Exception:
        flash("Lien invalide ou expiré.", category="danger")

    next_url = request.args.get("next") or url_for("owner_bp.dashboard")
    return redirect(next_url)


@auth_bp.route("/google/")
def google_login():
    CONF_URL = current_app.config.get("GOOGLE_CONF_URL")
    CLIENT_ID = current_app.config.get("GOOGLE_CLIEND_ID")
    CLIENT_SECRET = current_app.config.get("GOOGLE_SECRET_KEY")

    oauth.register(
        name="google",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        server_metadata_url=CONF_URL,
        client_kwargs={"scope": "openid email profile"},
    )
    redirect_uri = url_for("auth_bp.google_auth", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route("/google/auth/")
def google_auth():
    token = oauth.google.authorize_access_token()
    user_info = token["userinfo"]
    session["user"] = user_info
    # Logic to login or create user from google info
    return redirect("/dashboard/index/")


@auth_bp.get("/logout/")
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté(e).", category="info")
    session.clear()
    return redirect(url_for("auth_bp.login"))
