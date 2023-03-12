from flask import abort
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import logout_user
from src import csrf
from src.auth.models import VNUser
from src.dashboard.forms import CompanySettingForm
from src.mixins.decorators import agency_required


agency_bp = Blueprint("agency_bp", __name__, url_prefix="/dashboard/")
csrf.exempt(agency_bp)


@agency_bp.route("/<string:uuid>/parametres/", methods=["GET", "POST"])
@login_required
@agency_required
def agency_setting(uuid):
    page_title = "Paramètres"
    form = CompanySettingForm()

    if request.method == "POST" and form.validate_on_submit():

        current_user.vn_gender = form.gender.data
        current_user.vn_fullname = form.fullname.data

        current_user.vn_cni_number = form.cni_number.data
        current_user.vn_phonenumber_two = form.phonenumber_two.data

        current_user.vn_agencie_name = form.agencie_name.data
        current_user.vn_business_number = form.business_number.data

        current_user.vn_location = form.location.data
        current_user.vn_device = form.devise.data

        current_user.save()
        flash("Votre compte a été mise à jour avec succès.", "success")
        return redirect(url_for("agency_bp.agency_setting", uuid=current_user.uuid))
    elif request.method == "GET":
        form.gender.data = current_user.vn_gender
        form.fullname.data = current_user.vn_fullname

        form.cni_number.data = current_user.vn_cni_number
        form.phonenumber_two.data = current_user.vn_phonenumber_two

        form.agencie_name.data = current_user.vn_agencie_name
        form.business_number.data = current_user.vn_business_number

        form.location.data = current_user.vn_location
        form.devise.data = current_user.vn_device

    return render_template(
        "dashboard/account/company/settings.html",
        page_title=page_title,
        form=form,
        current_user=current_user,
    )


@agency_bp.get("/<string:uuid>/tenants/")
@login_required
def agency_create_tenant(uuid):
    page_title = "Vos locataires"

    return render_template(
        "tenant/tenant.html",
        page_title=page_title,
        current_user=current_user,
    )


@agency_bp.get("/<string:uuid>/houses/")
@login_required
def agency_house_list(uuid):
    page_title = "Propriétés"

    return render_template(
        "tenant/house.html",
        page_title=page_title,
        current_user=current_user,
    )


@agency_bp.get("/<string:uuid>/homeowners/")
@login_required
@agency_required
def agency_owner_list(uuid):
    page_title = "Vos bailleurs"

    return render_template(
        "tenant/owner.html",
        page_title=page_title,
        current_user=current_user,
    )


@agency_bp.route("/<string:uuid>/delete_account/", methods=["POST"])
@login_required
def delete_account(uuid):
    user = VNUser.query.filter_by(uuid=uuid).first()
    if current_user != user:
        abort(400)
    try:
        user.disable()
        logout_user()
        session.clear()
        flash("Votre compte a été supprimé avec succès !", category="success")
        return redirect(url_for("auth_bp.login"))
    except Exception as e:
        print(f"Une erreur s'est produite: {e}")
        abort(500)
