from flask import (
    render_template,
    redirect,
    request,
    flash,
    url_for,
    abort,
    current_app,
    send_from_directory,
)

from . import auth_view
from ... import login_manager
from flask_login import current_user, login_user, logout_user, login_required

from ..models import VNUser

from ..forms.auth_forms import OwnerHouseSignupForm, LoginForm


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@auth_view.route('/unconfirmed', strict_slashes=False)
def unconfirmed():
    if current_user.is_anonymous() or current_user.vn_user_activated:
        return redirect("venone.app")
    return render_template('auth/unconfirmed.html')


@auth_view.route('/login', methods=['POST', 'GET'], strict_slashes=False)
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = form.get_user()
        login_user(user)
        current_user.ping()
        flash("Logged in successfully.")
        return redirect(request.args.get('next') or url_for('dashbord.index'))
    return render_template('auth/login.html', form=form)


@auth_view.route('/logout', strict_slashes=False)
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('dashbord.index'))


@auth_view.route("/register/houseowner", methods=["GET", "POST"], strict_slashes=False)
def registerowner_page():

    if current_user.is_authenticated:
        return redirect(url_for('dashbord.index'))

    form = OwnerHouseSignupForm()
    if form.validate_on_submit():
        try:
            user = VNUser()
            form.populate_obj(user)
            user.save()
            msg_success = f"""
                Hey {form.email.data},
                votre compte a été créé ! Connectez-vous maintenant !
            """
            login_user(user)
            flash(msg_success, "success")
            return redirect(url_for("auth.login_page"))
        except Exception as e:
            return f"Une erreur s'est produite: {e}"

    page_title = "Inscription"

    return render_template("auth/signup/agencie.html", **locals())
