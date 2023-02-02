from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import Blueprint
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from ... import db
from ...mixins.email import send_email
from ..forms.agencie_form import AgencieSignupForm
from ..forms.auth_form import ChangeEmailForm
from ..forms.auth_form import ChangePasswordForm
from ..forms.auth_form import LoginForm
from ..forms.auth_form import PasswordResetForm
from ..forms.auth_form import PasswordResetRequestForm
from ..forms.owner_form import OwnerHouseSignupForm
from ..models import VNUser


auth_view = Blueprint("auth_view", __name__, url_prefix="/auth/customer/")


@auth_view.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.vn_user_activated and request.blueprint != "auth_view":
            return redirect(url_for("auth_view.unactivated"))


@auth_view.route("/unactivated/")
def unactivated():
    if current_user.is_anonymous or current_user.vn_user_activated:
        return redirect(url_for("auth_view.login"))
    return render_template("auth/unconfirmed.html")


@auth_view.route("/login/", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated and current_user.vn_user_activated:
        return redirect(url_for("dashboard_view.dashboard_view"))

    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        email_lower = form.addr_email.data.lower()
        user = (
            db.session.query(VNUser).filter_by(
                vn_user_addr_email=email_lower).first()
        )
        if user:
            if not user.vn_user_activated:
                flash(
                    """Vous n'êtes autorisé à accéder au système !
                    Veuillez contacter l'administrateur du système.""",
                    category="danger",
                )
            elif not user.verify_password(form.password.data):
                flash("Le mot de passe invalide.", category="danger")
            else:
                login_user(user, form.remember_me.data)
                next_page = request.args.get("next")
                flash(
                    f"Hello, bienvenu(e) sur votre tableau de bord: {user.vn_user_fullname}",
                    category="success",
                )
                if next_page is None or not next_page.startswith("/"):
                    next_page = url_for("dashboard_view.dashboard")
                return redirect(next_page)
        else:
            flash(
                "L'utilisateur n'existe pas ou le compte à été désactivé ! \
                Veuillez contacter l'administrateur système.",
                category="danger",
            )

    page_title = "Se connecter"
    return render_template("auth/login.html", page_title=page_title, form=form)


@auth_view.route("/owner/signup/", methods=["POST", "GET"])
def registerowner_page():

    if current_user.is_authenticated and current_user.vn_user_activated:
        if current_user.vn_user_account_type == 4:
            flash("Vous êtes déjà inscrit(e).", category="info")
            return redirect(url_for("dashboard_view.dashboard"))
        elif current_user.vn_user_account_type == 6:
            flash("Vous êtes déjà inscrit(e).", category="info")
            return redirect(url_for("dashboard_view.dashboard"))

    form = OwnerHouseSignupForm()
    if request.method == "POST" and form.validate_on_submit():
        user_to_create = VNUser(
            vn_user_gender=form.gender.data,
            vn_user_fullname=form.fullname.data,
            vn_user_addr_email=form.addr_email.data,
            vn_user_phonenumber_one=form.phonenumber_one.data,
            vn_user_cni_number=form.cni_number.data,
            vn_user_country=form.country.data,
        )
        user_to_create.set_password(form.password.data)
        user_to_create.vn_user_activated = True
        user_to_create.vn_user_account_type = 4
        user_to_create.save()
        msg_success = f"""
                Hey {user_to_create.vn_user_fullname},
                votre compte a été créé ! Connectez-vous maintenant !
            """
        flash(msg_success, "success")
        return redirect(url_for("auth_view.login"))

    page_title = "Créer un compte particulier"
    return render_template("auth/signup/owner.html", form=form, page_title=page_title)


@auth_view.route("/agencie/signup/", methods=["POST", "GET"])
def agencieregister_page():

    if current_user.is_authenticated and current_user.vn_user_activated:
        if current_user.vn_user_account_type == 4:
            flash("Vous êtes déjà inscrit(e).", category="info")
            return redirect(url_for("dashboard_view.dashboard"))
        elif current_user.vn_user_account_type == 6:
            flash("Vous êtes déjà inscrit(e).", category="info")
            return redirect(url_for("dashboard_view.dashboard"))

    form = AgencieSignupForm()
    if request.method == "POST" and form.validate_on_submit():
        user_to_create = VNUser(
            vn_user_gender=form.gender.data,
            vn_user_fullname=form.fullname.data,
            vn_user_addr_email=form.addr_email.data,
            vn_user_phonenumber_one=form.phonenumber_one.data,
            vn_business_number=form.business_number.data,
            vn_agencie_name=form.agencie_name.data,
            vn_user_country=form.country.data,
        )
        user_to_create.set_password(form.password.data)
        user_to_create.vn_user_activated = True
        user_to_create.vn_user_account_type = 6
        user_to_create.save()
        msg_success = f"""
            Hey {user_to_create.vn_user_fullname},
            votre compte a été créé ! Connectez-vous maintenant !
        """
        flash(msg_success, category="success")
        return redirect(url_for("auth_view.login"))

    page_title = "Créer un compte entreprise"
    return render_template("auth/signup/agencie.html", form=form, page_title=page_title)


@auth_view.route("/logout/")
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté(e).", category="info")
    session.clear()
    return redirect(url_for("auth_view.login"))


@auth_view.route("/changepassword/", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if request.method == "POST" and form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.vn_user_password = form.password_one.data
            current_user.save()
            flash("Votre mot de passe a été mis à jour.", category="success")
            return redirect(url_for("auth_view.change_password"))
        else:
            flash("Le mot de passe est invalide.", category="danger")

    page_title = "Changer votre mot de passe."
    return render_template(
        "auth/change_password.html", page_title=page_title, form=form
    )


@auth_view.route("/resetpassword/", methods=["GET", "POST"])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for("dashboard_view.dashboard"))

    form = PasswordResetRequestForm()
    if request.method == "POST" and form.validate_on_submit():
        email_lower = form.addr_email.data.lower()
        user = (
            db.session.query(VNUser).filter_by(vn_user_addr_email=email_lower).first()
        )
        if user:
            token = user.generate_reset_token()
            send_email(
                user.vn_user_addr_email,
                "Réinitialiser votre mot de passe",
                "auth/email/reset_password",
                user=user,
                token=token,
            )
            flash(
                """Un courriel contenant les instructions pour
                réinitialiser votre mot de passe vous a été envoyé.""",
                category="info",
            )
            return redirect(url_for("auth_view.login"))
        flash(
            f"""L'utilisateur avec l'adresse e-mail '{email_lower}!r'
            n'existe pas ou le compte a été désactivé !
            Veuillez contacter l'administrateur.""",
            category="danger",
        )

    page_title = "Réinitialiser votre mot de passe"
    return render_template("auth/reset_password.html", page_title=page_title, form=form)


@auth_view.route("/resetpassword/<token>/", methods=["GET", "POST"])
def password_reset(token):
    if current_user.is_authenticated:
        return redirect(url_for("dashboard_view.dashboard"))

    user = VNUser.verify_reset_password_token(token)

    if not user:
        return redirect(url_for("dashboard_view.dashboard"))

    form = PasswordResetForm()
    if form.validate_on_submit():
        user.password(form.password_one.data)
        db.session.commit()
        flash("Votre mot de passe a été mis à jour.", category="success")
        return redirect(url_for("auth_view.login"))

    page_title = "Réinitialiser votre mot de passe"
    return render_template(
        "auth/change_password.html", page_title=page_title, form=form
    )


@auth_view.route("/changeemail/", methods=["GET", "POST"])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.addr_email.data.lower()
            token = current_user.generate_email_change_token(new_email)
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
            return redirect(url_for("dashboard_view.dashboard"))
        else:
            flash("Courriel ou mot de passe non valide.")

    page_title = "Confirmez votre adresse électronique"
    return render_template("auth/change_email.html", page_title=page_title, form=form)


@auth_view.route("/changeemail/<token>/", methods=["GET"])
@login_required
def change_email(token):
    if current_user.change_email(token):
        db.session.commit()
        flash("Votre adresse e-mail a été mise à jour.")
    else:
        flash("Demande invalide.")
    return redirect(url_for("dashboard_view.dashboard"))
