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
from src.tenant import HouseOwnerForm
from src.tenant import VNHouse
from src.tenant import VNHouseOwner
from src.tenant import VNTenant

agency_bp = Blueprint("agency_bp", __name__, url_prefix="/dashboard/")


@agency_bp.route("/api/", methods=["GET"])
@login_required
def api():
    from flask import jsonify

    data = {"id": current_user.id, "addr_email": current_user.vn_addr_email}
    return jsonify({"data": data}), 200


@agency_bp.route("/<string:uuid>/settings/", methods=["GET", "POST"])
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

    return render_template(
        "auth/admin/pages/company/settings.html",
        page_title=page_title,
        form=form,
        current_user=current_user,
    )


@agency_bp.route("/<string:uuid>/houseowners/", methods=["GET", "POST"])
@login_required
@check_activated
@agency_required
def house_owner_list(uuid):
    page_title = "Liste de vos propriétaires de maison"
    houseowners = VNHouseOwner.houseowner_list_query()
    form = HouseOwnerForm()
    if request.method == "POST" and form.validate_on_submit():

        houseowner = VNHouseOwner(
            vn_gender=form.gender.data,
            vn_fullname=form.fullname.data,
            vn_addr_email=form.addr_email.data,
            vn_cni_number=form.cni_number.data,
            vn_profession=form.profession.data,
            vn_parent_name=form.parent_name.data,
            vn_location=form.location.data,
            vn_phonenumber_one=form.phonenumber_one.data,
            vn_phonenumber_two=form.phonenumber_two.data,
        )
        houseowner.vn_user_id = current_user.id
        houseowner.save()
        return redirect(url_for("agency_bp.house_owner_list", uuid=current_user.uuid))

    return render_template(
        "tenant/list.html",
        form=form,
        page_title=page_title,
        houseowners=houseowners,
        current_user=current_user,
    )


@agency_bp.route("/<string:uuid>/create_house_owner/", methods=["GET", "POST"])
@login_required
@check_activated
@agency_required
def create_house_owner(uuid):
    page_title = "Enregistrer un propriétaire de maison"
    form = HouseOwnerForm()
    if request.method == "POST" and form.validate_on_submit():

        houseowner = VNHouseOwner(
            vn_gender=form.gender.data,
            vn_fullname=form.fullname.data,
            vn_addr_email=form.addr_email.data,
            vn_cni_number=form.cni_number.data,
            vn_profession=form.profession.data,
            vn_parent_name=form.parent_name.data,
            vn_location=form.location.data,
            vn_phonenumber_one=form.phonenumber_one.data,
            vn_phonenumber_two=form.phonenumber_two.data,
        )
        houseowner.vn_user_id = current_user.id
        houseowner.save()
        return redirect(url_for("agency_bp.house_owner_list", uuid=current_user.uuid))

    return render_template(
        "tenant/create.html",
        form=form,
        page_title=page_title,
        current_user=current_user,
    )


@agency_bp.route("/<string:owner_uuid>/delete_house_owner/")
@login_required
@check_activated
@agency_required
def delete_house_owner(owner_uuid):
    owner = VNHouseOwner.get_houseowner(owner_uuid)
    owner.desactivate()
    flash(
        f"Le propriétaire {owner.vn_fullname} a été retiré avec succès !",
        category="success",
    )
    return redirect(url_for("agency_bp.house_owner_list", uuid=current_user.uuid))
