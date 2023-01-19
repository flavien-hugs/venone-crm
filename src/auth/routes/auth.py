from flask import flash
from flask import session
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from werkzeug.security import generate_password_hash

from . import auth_view
from ... import db
from ... import login_manager
from ..forms.auth_form import LoginForm
from ..forms.owner_form import OwnerHouseSignupForm
from ..models import VNUser


@login_manager.user_loader
def load_user(user_id):
    return VNUser.query.get(int(user_id))


@auth_view.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.vn_user_activated and request.blueprint != "auth_view":
            return redirect(url_for("auth_view.unactivated"))


@auth_view.route("/unactivated")
def unactivated():
    if current_user.is_anonymous or current_user.vn_user_activated:
        return redirect(url_for("auth_view.login"))
    return render_template("auth/unconfirmed.html")


@auth_view.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = (
            VNUser.query\
                .filter_by(vn_user_addr_email=form.addr_email.data.lower()).first()
        )
        if user:
            if not user.vn_user_activated:
                flash(
                    """L'utilisateur n'a pas été autorisé à accéder au système !
                    Veuillez contacter l'administrateur du système""", 'danger'
                )
            elif not user.verify_password(form.password.data):
                flash('Mot de passe invalide', 'danger')
            else:
                login_user(user, form.remember_me.data)
                next_page = request.args.get("next")
                return redirect(next_page) if next_page else redirect(url_for('owner_view.owner_dashboard'))
        else:
            flash(
                "L'utilisateur n'existe pas ! Veuillez contacter l'administrateur système",
                "danger"
            )

    return render_template("auth/login.html", form=form)


@auth_view.route("/register/houseowner", methods=["POST", "GET"])
def registerowner_page():

    if current_user.is_authenticated and current_user.vn_user_account_type == 4:
        return redirect(url_for("owner_view.owner_dashboard"))

    if current_user.is_authenticated and current_user.vn_user_account_type == 6:
        pass

    form = OwnerHouseSignupForm()
    if form.validate_on_submit():
        try:
            user = VNUser(
                vn_user_gender=form.gender.data,
                vn_user_fullname=form.fullname.data,
                vn_user_addr_email=form.addr_email.data,
                vn_user_phonenumber_one=form.phonenumber_one.data,
                vn_user_cni_number=form.cni_number.data,
                vn_user_country=form.country.data,
            )
            user.vn_user_password = generate_password_hash(form.password.data)
            user.vn_user_activated = True
            user.vn_user_account_type = 4
            user.save()
            msg_success = f"""
                Hey {form.addr_email.data}, votre compte a été créé ! Connectez-vous maintenant !
            """
            # login_user(user)
            flash(msg_success, "success")
            return redirect(url_for("auth_view.login"))
        except Exception as e:
            return f"Une erreur s'est produite: {e}"

    page_title = "Créer un compte particulier"

    return render_template("auth/signup/owner.html", form=form, page_title=page_title)


@auth_view.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté(e).")
    session.clear()
    return redirect(url_for("auth_view.login"))
