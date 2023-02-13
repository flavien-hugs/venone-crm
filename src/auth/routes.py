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
from src import db
from src.auth.forms.agencie_form import AgencieSignupForm
from src.auth.forms.auth_form import ChangeEmailForm
from src.auth.forms.auth_form import LoginForm
from src.auth.forms.auth_form import PasswordResetForm
from src.auth.forms.auth_form import PasswordResetRequestForm
from src.auth.forms.owner_form import OwnerHouseSignupForm
from src.auth.models import VNUser
from src.mixins.email import send_email

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth/customer/")


@auth_bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.vn_activated and request.blueprint != "auth_bp":
            return redirect(url_for("auth_bp.unactivated"))


@auth_bp.route("/unactivated/")
@login_required
def unactivated():
    if current_user.vn_activated:
        return redirect(url_for("auth_bp.login"))
    return render_template("auth/unconfirmed.html")


@auth_bp.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        email_lower = form.addr_email.data.lower()
        user = VNUser.query.filter_by(vn_addr_email=email_lower).first()
        if user:
            if not user.vn_activated:
                flash(
                    """Vous n'êtes autorisé à accéder au système !
                    Veuillez contacter l'administrateur du système.""",
                    category="danger",
                )
            elif not user.verify_password(form.password.data):
                flash("Le mot de passe invalide.", category="danger")
            else:

                login_user(user, form.remember_me.data)
                flash(
                    f"Hello, bienvenue sur votre tableau de bord: {user.vn_fullname!r}",
                    category="success",
                )
                return redirect(
                    request.args.get("next")
                    or url_for("owner_bp.dashboard", uuid=user.uuid)
                )
        else:
            flash(
                "L'utilisateur n'existe pas ou le compte à été désactivé ! \
                Veuillez contacter l'administrateur système.",
                category="danger",
            )

    page_title = "Se connecter"
    return render_template("auth/login.html", page_title=page_title, form=form)


@auth_bp.route("/owner/signup/", methods=["POST", "GET"])
def registerowner_page():

    if current_user.is_authenticated and current_user.vn_activated:
        flash("Vous êtes déjà inscrit(e).", category="info")
        return redirect(url_for("owner_bp.dashboard", uuid=current_user.uuid))

    form = OwnerHouseSignupForm()
    if request.method == "POST" and form.validate_on_submit():
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


@auth_bp.route("/company/signup/", methods=["POST", "GET"])
def agencieregister_page():

    if current_user.is_authenticated and current_user.vn_activated:
        flash("Vous êtes déjà inscrit(e).", category="info")
        return redirect(url_for("owner_bp.dashboard", uuid=current_user.uuid))

    form = AgencieSignupForm()
    if request.method == "POST" and form.validate_on_submit():
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


@auth_bp.route("/reset_password/", methods=["GET", "POST"])
def password_reset_request():

    form = PasswordResetRequestForm()
    if request.method == "POST" and form.validate_on_submit():
        email_lower = form.addr_email.data.lower()
        user = VNUser.query.filter_by(vn_addr_email=email_lower).first()
        if user:
            token = user.generate_reset_token()
            send_email(
                user.vn_addr_email,
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
            return redirect(url_for("auth_bp.login"))
        flash(
            f"""L'utilisateur avec l'adresse e-mail '{email_lower}!r'
            n'existe pas ou le compte a été désactivé !
            Veuillez contacter l'administrateur.""",
            category="danger",
        )

    page_title = "Réinitialiser votre mot de passe"
    return render_template("auth/reset_password.html", page_title=page_title, form=form)


@auth_bp.route("/resetpassword/<token>/", methods=["GET", "POST"])
def password_reset(token):
    if current_user.is_authenticated:
        if current_user.vn_house_owner:
            flash("Vous êtes déjà inscrit(e).", category="info")
            return redirect(url_for("owner_bp.dashboard"))
        elif current_user.vn_company:
            flash("Vous êtes déjà inscrit(e).", category="info")
            return redirect(url_for("agency_bp.dashboard"))

    user = VNUser.verify_reset_password_token(token)

    if not user:
        return redirect(url_for("auth_bp.login"))

    form = PasswordResetForm()
    if form.validate_on_submit():
        user.password(form.new_password.data)
        db.session.commit()
        flash("Votre mot de passe a été mis à jour.", category="success")
        return redirect(url_for("auth_bp.login"))

    page_title = "Réinitialiser votre mot de passe"
    return render_template(
        "auth/change_password.html", page_title=page_title, form=form
    )


@auth_bp.route("/change_email/", methods=["GET", "POST"])
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
            next_url = request.args.get("next")
            return redirect(next_url)
        else:
            flash("Courriel ou mot de passe non valide.")

    page_title = "Confirmez votre adresse électronique"
    return render_template("auth/change_email.html", page_title=page_title, form=form)


@auth_bp.route("/change_email/<token>/", methods=["GET"])
@login_required
def change_email(token):
    if current_user.change_email(token):
        db.session.commit()
        flash("Votre adresse e-mail a été mise à jour.")
    else:
        flash("Demande invalide.")
    next_url = request.args.get("next")
    return redirect(next_url)


@auth_bp.route("/logout/")
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté(e).", category="info")
    session.clear()
    return redirect(url_for("auth_bp.login"))
