from flask import Blueprint
from flask import request, redirect, url_for, flash
from flask import render_template
from flask_login import current_user
from flask_login import login_required

from src import db
from src.auth.models import VNUser

from src.mixins.decorators import check_activated, owner_required
from src.dashboard.forms import OwnerSettingForm
from src.auth.forms.auth_form import ChangePasswordForm

owner_bp = Blueprint("owner_bp", __name__, url_prefix="/dashboard/owner/")


@owner_bp.route("/api/", methods=["GET"])
@login_required
def api():
    from flask import jsonify
    data = {
        "id": current_user.id,
        "addr_email": current_user.vn_user_addr_email
    }
    return jsonify({"data": data}), 200


@owner_bp.route("/index/", methods=["GET"])
@login_required
@owner_required
@check_activated
def dashboard():
    page_title = "Tableau de board"
    return render_template(
        "auth/admin/dashboard.html",
        page_title=page_title,
        current_user=current_user
    )


@owner_bp.route("/settings/", methods=["GET", "POST"])
@login_required
@owner_required
@check_activated
def owner_setting():
    page_title = "Paramètres"
    form = OwnerSettingForm()
    if request.method == "POST" and form.validate_on_submit():
        current_user.vn_user_gender = form.gender.data
        current_user.vn_user_fullname = form.fullname.data

        current_user.vn_user_cni_number = form.cni_number.data
        current_user.vn_user_phonenumber_two = form.phonenumber_two.data

        current_user.vn_user_profession = form.profession.data
        current_user.vn_user_parent_name = form.parent_name.data

        current_user.vn_user_location = form.location.data
        current_user.vn_user_birthdate = form.birthdate.data

        current_user.save()
        flash("Votre compte a été mise à jour avec succès.", "success")
        return redirect(url_for('owner_bp.owner_setting'))
    elif request.method == 'GET':

        form.gender.data = current_user.vn_user_gender
        form.fullname.data = current_user.vn_user_fullname

        form.cni_number.data = current_user.vn_user_cni_number
        form.phonenumber_two.data = current_user.vn_user_phonenumber_two

        form.profession.data = current_user.vn_user_profession
        form.parent_name.data = current_user.vn_user_parent_name

        form.location.data = current_user.vn_user_location
        form.birthdate.data = current_user.vn_user_birthdate

    return render_template(
        "auth/admin/pages/owner/settings.html",
        page_title=page_title,
        form=form,
        current_user=current_user
    )


@owner_bp.route("/changepaswword/", methods=["GET", "POST"])
@login_required
@check_activated
def change_password():
    page_title = "Changer votre mot de passe"
    form = ChangePasswordForm()
    if request.method == "POST" and form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.vn_user_password = form.new_password.data
            current_user.set_password(form.new_password.data)
            current_user.save()
            flash("Votre mot de passe a été mise à jour avec succès.", "success")
            return redirect(request.path)
        else:
            flash("Le mot de passe est invalide.", category="danger")

    return render_template(
        "auth/admin/pages/password.html",
        page_title=page_title,
        form=form,
        current_user=current_user
    )
