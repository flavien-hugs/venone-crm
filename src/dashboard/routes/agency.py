from flask import Blueprint
from flask import request, redirect, url_for, flash
from flask import render_template
from flask_login import current_user
from flask_login import login_required

from src import db
from src.auth.models import VNUser
from src.dashboard.forms import CompanySettingForm
from src.mixins.decorators import check_activated, agency_required


agency_bp = Blueprint("agency_bp", __name__, url_prefix="/dashboard/company/")


@agency_bp.route("/api/", methods=["GET"])
@login_required
def api():
    from flask import jsonify
    data = {
        "id": current_user.id,
        "addr_email": current_user.vn_user_addr_email
    }
    return jsonify({"data": data}), 200


@agency_bp.route("/index/", methods=["GET"])
@login_required
@check_activated
@agency_required
def dashboard():
    page_title = "Tableau de board"
    return render_template(
        "auth/admin/dashboard.html",
        page_title=page_title,
        current_user=current_user
    )


@agency_bp.route("/settings/", methods=["GET"])
@login_required
@check_activated
@agency_required
def agency_setting():
    page_title = "Paramètres"
    form = CompanySettingForm()
    if request.method == "POST" and form.validate_on_submit():
        current_user.vn_user_gender = form.gender.data
        current_user.vn_user_fullname = form.fullname.data

        current_user.vn_user_cni_number = form.cni_number.data
        current_user.vn_user_phonenumber_two = form.phonenumber_two.data

        current_user.vn_agencie_name = form.agencie_name.data
        current_user.vn_business_number = form.business_number.data

        current_user.vn_user_location = form.location.data

        current_user.save()
        flash("Votre compte a été mise à jour avec succès.", "success")
        return redirect(url_for('owner_bp.agency_setting'))
    elif request.method == 'GET':

        form.gender.data = current_user.vn_user_gender
        form.fullname.data = current_user.vn_user_fullname

        form.cni_number.data = current_user.vn_user_cni_number
        form.phonenumber_two.data = current_user.vn_user_phonenumber_two

        form.agencie_name.data = current_user.vn_agencie_name
        form.business_number.data = current_user.vn_business_number

        form.location.data = current_user.vn_user_location

    return render_template(
        "auth/admin/pages/company/settings.html",
        page_title=page_title,
        form=form,
        current_user=current_user
    )
