from flask import Blueprint
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from src import cache
from src import csrf
from src.auth.forms.auth_form import ChangePasswordForm
from src.dashboard.forms import OwnerSettingForm
from src.mixins.decorators import owner_required
from src.tenant import tasks
from src.tenant import VNHouse

owner_bp = Blueprint("owner_bp", __name__, url_prefix="/dashboard/")
csrf.exempt(owner_bp)


@owner_bp.route("/<string:uuid>/index/", methods=["GET"])
@login_required
def dashboard(uuid):
    page_title = "Tableau de board"
    VNHouse.update_expired_lease_end_dates()
    tasks.payment_reminders.apply_async()
    return render_template(
        "dashboard/dashboard.html", page_title=page_title, current_user=current_user
    )


@owner_bp.route("/<string:uuid>/parameters/", methods=["GET", "POST"])
@login_required
@owner_required
def owner_setting(uuid):
    page_title = "Paramètres"
    form = OwnerSettingForm()

    if request.method == "POST" and form.validate_on_submit():

        current_user.vn_gender = form.gender.data
        current_user.vn_fullname = form.fullname.data

        current_user.vn_cni_number = form.cni_number.data
        current_user.vn_phonenumber_two = form.phonenumber_two.data

        current_user.vn_profession = form.profession.data
        current_user.vn_parent_name = form.parent_name.data

        current_user.vn_device = form.devise.data
        current_user.vn_location = form.location.data
        current_user.vn_birthdate = form.birthdate.data

        current_user.save()
        flash("Votre compte a été mise à jour avec succès.", "success")
        return redirect(url_for("owner_bp.owner_setting", uuid=current_user.uuid))
    elif request.method == "GET":

        form.gender.data = current_user.vn_gender
        form.fullname.data = current_user.vn_fullname

        form.cni_number.data = current_user.vn_cni_number
        form.phonenumber_two.data = current_user.vn_phonenumber_two

        form.profession.data = current_user.vn_profession
        form.parent_name.data = current_user.vn_parent_name

        form.devise.data = current_user.vn_device
        form.location.data = current_user.vn_location
        form.birthdate.data = current_user.vn_birthdate

    return render_template(
        "dashboard/account/owner/settings.html",
        page_title=page_title,
        form=form,
        current_user=current_user,
    )


@owner_bp.route("/<string:uuid>/change_paswword/", methods=["GET", "POST"])
@login_required
def change_password(uuid):
    page_title = "Changer votre mot de passe"
    form = ChangePasswordForm()
    if request.method == "POST" and form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.vn_password = form.new_password.data
            current_user.set_password(form.new_password.data)
            current_user.save()
            flash("Votre mot de passe a été mise à jour avec succès.", "success")
            return redirect(url_for("owner_bp.change_password", uuid=current_user.uuid))
        else:
            flash("Le mot de passe est invalide.", category="danger")

    return render_template(
        "dashboard/account/password.html",
        page_title=page_title,
        form=form,
        current_user=current_user,
    )


@owner_bp.route("/<filename>/")
@cache.cached(timeout=100)
def avatar(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER_PATH"], filename)
