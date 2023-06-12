from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from src.auth import utils
from src.auth.forms.agencie_form import AgencieSignupForm
from src.auth.forms.auth_form import ChangeEmailForm
from src.auth.forms.auth_form import LoginForm
from src.auth.forms.auth_form import PasswordResetForm
from src.auth.forms.auth_form import PasswordResetRequestForm
from src.auth.forms.owner_form import OwnerHouseSignupForm
from src.auth.models import VNUser
from src.exts import db
from src.exts import login_manager
from src.mixins.email import send_email

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth/")


@login_manager.unauthorized_handler
def unauthorized():
    flash("Vous devez être connecté pour voir cette page.")
    return redirect(url_for("auth_bp.login"))


@auth_bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()


@auth_bp.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("owner_bp.dashboard"))

    form = LoginForm(request.form)
    if form.validate_on_submit():
        email_or_phone = form.email_or_phone.data
        user = VNUser.find_by_email_and_phone(email_or_phone)
        if user and user.vn_activated and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next_page = request.args.get("next")
            if next_page is None or not next_page.startswith("/"):
                next_page = url_for("owner_bp.dashboard")
            flash(
                f"Hello, bienvenue sur votre tableau de bord: {user.vn_fullname!r}",
                category="success",
            )
            return redirect(next_page)
        else:
            if not user.vn_activated:
                error_message = "L'utilisateur n'existe pas ou le compte a\
                    été désactivé ! Veuillez contacter l'administrateur système."
            if not user.verify_password(form.password.data):
                error_message = "Le mot de passe invalide."

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
        user_to_create = VNUser(
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
        user_to_create.save()
        msg_success = f"""
            Hey {user_to_create.vn_fullname},
            votre compte a été créé ! Connectez-vous maintenant !
        """
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
        user_to_create = VNUser(
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
        user_to_create.save()
        msg_success = f"""
            Hey {user_to_create.vn_fullname},
            votre compte a été créé ! Connectez-vous maintenant !
        """
        flash(msg_success, category="success")
        return redirect(url_for("auth_bp.login"))

    page_title = "Créer un compte entreprise"
    return render_template("auth/signup/agencie.html", form=form, page_title=page_title)


@auth_bp.route("/reset-password/", methods=["GET", "POST"])
def password_reset_request():
    form = PasswordResetRequestForm(request.form)
    if form.validate_on_submit():
        email = form.addr_email.data.lower()
        user = VNUser.find_by_email(email)
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
                """Nous venons de vous envoyer un e-mail avec\
                    un lien pour réinitialiser votre mot de passe !""",
                category="info",
            )
            return redirect(url_for("auth_bp.login"))
        else:
            flash(
                f"""L'adresse e-mail '{email}!r' n'est pas enregistrée ou\
                    le compte a été désactivé ! Veuillez contacter l'administrateur.""",
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

    user = VNUser.find_by_email(email)
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
                "Votre mot de passe a été réinitialisé avec succès.\
                    Vous pouvez maintenant vous connecter.",
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
                "Un courriel contenant des instructions pour confirmer\
                    votre nouvelle adresse électronique vous a été envoyé.",
                category="info",
            )
            next_url = request.args.get("next")
            return redirect(next_url)
        else:
            flash("Courriel ou mot de passe non valide.", category="danger")

    page_title = "Confirmez votre adresse électronique"
    return render_template("auth/change_email.html", page_title=page_title, form=form)


@auth_bp.get("/change-email/<token>/")
@login_required
def change_email(token):
    if utils.confirm_token(token):
        db.session.commit()
        flash("Votre adresse e-mail a été mise à jour.", category="info")
    else:
        flash("Demande invalide.", category="danger")
    next_url = request.args.get("next")
    return redirect(next_url)


@auth_bp.get("/logout/")
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté(e).", category="info")
    session.clear()
    return redirect(url_for("auth_bp.login"))
