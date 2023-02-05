from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from src.dashboard.forms import CompanySettingForm
from src.mixins.decorators import agency_required
from src.mixins.decorators import check_activated

from src import csrf

agency_bp = Blueprint("agency_bp", __name__, url_prefix="/dashboard/")


@agency_bp.route("/api/", methods=["GET"])
@login_required
def api():
    from flask import jsonify

    data = {"id": current_user.id, "addr_email": current_user.vn_user_addr_email}
    return jsonify({"data": data}), 200

@agency_bp.route("/<string:uuid>/parameters/", methods=["GET", "POST"])
@login_required
@agency_required
@check_activated
@csrf.exempt
def agency_setting(uuid):
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
        return redirect(url_for("agency_bp.agency_setting", uuid=current_user.uuid))
    elif request.method == "GET":
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
