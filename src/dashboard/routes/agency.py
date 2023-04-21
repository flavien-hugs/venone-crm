from datetime import datetime

from flask import abort
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import Response
from flask import session
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import logout_user
from src import csrf
from src.auth.models import VNUser
from src.dashboard.forms import CompanySettingForm
from src.dashboard.services import export_data
from src.mixins.decorators import agency_required
from src.payment import VNPayment
from src.tenant import VNHouse
from src.tenant import VNHouseOwner
from src.tenant import VNTenant


agency_bp = Blueprint("agency_bp", __name__, url_prefix="/dashboard/")
csrf.exempt(agency_bp)


@agency_bp.route("/parametres/", methods=["GET", "POST"])
@login_required
@agency_required
def agency_setting():
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
        return redirect(url_for("agency_bp.agency_setting"))
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


@agency_bp.get("/tenants/")
@login_required
def agency_create_tenant():
    page_title = "Vos locataires"

    return render_template(
        "tenant/tenant.html",
        page_title=page_title,
        current_user=current_user,
    )


@agency_bp.get("/billing/")
@login_required
@agency_required
def agency_billing():
    page_title = "Facturation"

    return render_template(
        "dashboard/account/billing.html",
        page_title=page_title,
        current_user=current_user,
    )


@agency_bp.get("/houses/")
@login_required
def agency_house_list():
    page_title = "Propriétés"

    return render_template(
        "tenant/house.html",
        page_title=page_title,
        current_user=current_user,
    )


@agency_bp.get("/homeowners/")
@login_required
@agency_required
def agency_owner_list():
    page_title = "Vos bailleurs"

    return render_template(
        "tenant/owner.html",
        page_title=page_title,
        current_user=current_user,
    )


@agency_bp.route("/delete_account/", methods=["POST"])
@login_required
def delete_account():
    user = VNUser.get_user_logged()
    if current_user != user:
        abort(400)
    try:
        user.disable()
        logout_user()
        session.clear()
        flash("Votre compte a été supprimé avec succès !", category="success")
        return redirect(url_for("auth_bp.login"))
    except Exception as e:
        abort(500, f"Une erreur s'est produite: {e}")


@agency_bp.get("/export-tenants-data/")
@login_required
def export_tenants_csv():

    headers = [
        "ID",
        "Nom & Prénoms",
        "N° Téléphone",
        "Adresse e-mail",
        "N° CNI",
        "Profession",
        "Loyer",
        "Date d'ajout",
    ]

    data = VNTenant.get_tenants_list()

    current_date = datetime.now().strftime("%Y-%m-%d_%H-%M")
    response = Response(
        export_data.generate_tenant_csv(data, headers), mimetype="text/csv"
    )

    response.headers.set(
        "Content-Disposition",
        "attachment",
        filename="tenants_data{}.csv".format(current_date),
    )
    return response


@agency_bp.get("/export-owners-data/")
@login_required
def export_owners_csv():

    headers = [
        "ID",
        "Nom & Prénoms",
        "N° Téléphone",
        "Adresse e-mail",
        "N° CNI",
        "Profession",
        "Nombre de propriétés",
        "Date d'ajout",
    ]

    owners = VNHouseOwner.get_owners_list()

    current_date = datetime.now().strftime("%Y-%m-%d_%H-%M")
    response = Response(
        export_data.generate_owner_csv(owners, headers), mimetype="text/csv"
    )

    response.headers.set(
        "Content-Disposition",
        "attachment",
        filename="owners_data_{}.csv".format(current_date),
    )
    return response


@agency_bp.get("/export-houses-data/")
@login_required
def export_houses_csv():

    headers = [
        "ID",
        "Propriétaire",
        "Type de propriété",
        "Loyer",
        "Caution",
        "Nombre de pièces",
        "Situation géographique",
        "Date de mise en location",
        "Disponibilité de la propriété",
        "Date d'ajout",
    ]

    owners = VNHouse.get_houses_list()

    current_date = datetime.now().strftime("%Y-%m-%d_%H-%M")
    response = Response(
        export_data.generate_house_csv(owners, headers), mimetype="text/csv"
    )

    response.headers.set(
        "Content-Disposition",
        "attachment",
        filename="houses_data_{}.csv".format(current_date),
    )
    return response


@agency_bp.get("/export-payments-data/")
@login_required
def export_payments_csv():

    headers = [
        "ID Transaction",
        "ID Opérateur",
        "Nom & prénom du locataire",
        "Loyer (montant)",
        "Méthode de paiement",
        "Date de paiement",
    ]

    payments = VNPayment.get_payment_list()

    current_date = datetime.now().strftime("%Y-%m-%d_%H-%M")
    response = Response(
        export_data.generate_payments_csv(payments, headers), mimetype="text/csv"
    )

    response.headers.set(
        "Content-Disposition",
        "attachment",
        filename="payments_data_{}.csv".format(current_date),
    )
    return response
