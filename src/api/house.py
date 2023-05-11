from datetime import datetime
from datetime import timedelta
from http import HTTPStatus

from flask import abort
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from src.auth.models import VNUser
from src.exts import db
from src.tenant import VNHouse
from src.tenant import VNTenant
from src.utils import jsonify_response

from . import api


@api.get("/houses/")
@login_required
@jsonify_response
def get_all_houses():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = VNHouse.get_houses_list().paginate(
        page=page, per_page=per_page, error_out=False
    )
    houses = pagination.items

    prev = (
        url_for("api.get_all_houses", page=page - 1, _external=True)
        if pagination.has_prev
        else None
    )
    next = (
        url_for("api.get_all_houses", page=page + 1, _external=True)
        if pagination.has_next
        else None
    )

    return {
        "houses": [house.to_json() for house in houses],
        "prev": prev,
        "next": next,
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "user": current_user.to_json(),
    }


def house_to_json(house):
    return {
        "house_id": house.vn_house_id,
        "house_type": house.vn_house_type,
        "house_month": house.vn_house_month,
        "house_guaranty": "{:,.2f}".format(house.vn_house_guaranty),
        "house_rent": "{:,.2f}".format(house.vn_house_rent),
        "house_devise": house.user_houses.vn_device,
        "house_number_room": house.vn_house_number_room,
        "house_address": house.vn_house_address,
        "house_country": house.user_houses.vn_country,
        "house_closed": house.vn_house_is_open,
        "created_at": house.vn_created_at.isoformat(),
    }


@api.get("/check-houses-country/")
@login_required
@jsonify_response
def get_houses_country():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 12, type=int)
    pagination, houses = VNUser.get_houses_by_country(page, per_page)

    prev = (
        url_for("api.get_houses_country", page=page - 1, _external=True)
        if pagination.has_prev
        else None
    )
    next = (
        url_for("api.get_houses_country", page=page + 1, _external=True)
        if pagination.has_next
        else None
    )
    return {
        "houses": [house_to_json(house) for house in houses],
        "prev": prev,
        "next": next,
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
    }


@api.get("/available-houses/")
@jsonify_response
def get_houses_listing():

    """
    Récupère une liste paginée des maisons disponibles.

    Args:
        page (int, optional): Le numéro de page à récupérer. Par défaut, 1.
        per_page (int, optional): Le nombre d'éléments par page. Par défaut, 10.

    Returns:
        dict: Un objet JSON contenant la liste des maisons disponibles.

    Raises:
        Aucune erreur n'est levée.

    Exemple:
        Pour récupérer la deuxième page contenant 20 éléments :
        /api/available-houses/?page=2&per_page=20
    """

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    houses = VNHouse.query.filter_by(vn_house_is_open=False).order_by(
        VNHouse.vn_created_at.desc()
    )

    pagination = houses.paginate(page=page, per_page=per_page)

    return {
        "houses": [house_to_json(house) for house in pagination.items],
    }


@api.get("/available-houses/<int:house_id>/")
@jsonify_response
def get_house_info(house_id):

    """
    Récupère les informations d'une maison disponible.

    Args:
        house_id (int): L'identifiant de la maison

    Returns:
        dict: Un objet JSON contenant les informations sur la maison disponible.

    Exemple:
        Pour récupérer les informations de la maison avec l'identifiant 123 :
        /api/available-houses/123/
    """

    house = VNHouse.query.filter_by(
        vn_house_id=house_id, vn_house_is_open=False
    ).first()

    if not house:
        abort(HTTPStatus.NOT_FOUND, "Could not find house.")

    return {"house": house_to_json(house)}


@api.get("/houses/<string:house_uuid>/")
@login_required
@jsonify_response
def get_house(house_uuid):

    house = VNHouse.get_house(house_uuid)

    if not house:
        return {"error": "House not found"}

    tenants = house.tenants(page=request.args.get("page", 1, type=int))
    payments = house.payments(page=request.args.get("page", 1, type=int))

    return {
        "house": house.to_json(),
        "house_tenant": [t.to_json() for t in tenants.items],
        "house_tenants_pagination": {
            "page": tenants.page,
            "per_page": tenants.per_page,
            "total": tenants.total,
            "pages": tenants.pages,
        },
        "house_payment": [p.to_json() for p in payments.items],
        "house_payments_pagination": {
            "page": payments.page,
            "per_page": payments.per_page,
            "total": payments.total,
            "pages": payments.pages,
        },
    }


@api.patch("/houses/<string:house_uuid>/house-assign-tenant/")
@login_required
@jsonify_response
def house_assign_tenant(house_uuid):

    """
    Vue permettant d'assigner une propriété disponible
    à un locataire
    """

    house = VNHouse.get_house(house_uuid)

    if not house:
        return {"message": "maison introuvable"}

    house_data = request.json.get("house_data")
    tenant_data = request.json.get("tenant_data")

    house_type = house_data.get("house_type")
    house_rent = house_data.get("house_rent")
    house_guaranty = house_data.get("house_guaranty")
    house_month = house_data.get("house_month")
    house_number_room = house_data.get("house_number_room")
    house_address = house_data.get("house_address")
    lease_start_date = house_data.get("lease_start_date")

    house.vn_house_type = house_type
    house.vn_house_rent = house_rent
    house.vn_house_guaranty = house_guaranty
    house.vn_house_month = house_month
    house.vn_house_number_room = house_number_room
    house.vn_house_address = house_address
    house.vn_house_is_open = True

    house.vn_house_lease_start_date = (
        datetime.strptime(lease_start_date, "%Y-%m-%d").date()
        if lease_start_date
        else None
    )

    notice_period = timedelta(days=10)

    if lease_start_date:
        lease_end_date = (
            datetime.strptime(lease_start_date, "%Y-%m-%d")
            + timedelta(days=31)
            - notice_period
        ).date()

        if hasattr(house, "vn_house_lease_end_date"):
            house.vn_house_lease_end_date = lease_end_date
        else:
            raise AttributeError(
                "L'objet house doit avoir un attribut 'vn_house_lease_end_date'"
            )

    tenant = VNTenant()

    tenant.vn_fullname = tenant_data.get("fullname")
    tenant.vn_addr_email = tenant_data.get("addr_email")
    tenant.vn_cni_number = tenant_data.get("cni_number")
    tenant.vn_location = tenant_data.get("location")
    tenant.vn_profession = tenant_data.get("profession")
    tenant.vn_parent_name = tenant_data.get("parent_name")
    tenant.vn_phonenumber_one = tenant_data.get("phonenumber_one")
    tenant.vn_phonenumber_two = tenant_data.get("phonenumber_two")

    house.tenants.append(tenant)
    tenant.vn_owner_id = house.vn_owner_id
    tenant.vn_user_id = current_user.id

    db.session.add_all([house, tenant])
    db.session.commit()

    return {
        "success": True,
        "message": "Nouveau locataire ajouté avec succès",
    }


@api.put("/houses/<string:house_uuid>/update/")
@login_required
@jsonify_response
def update_house(house_uuid):
    house = VNHouse.get_house(house_uuid)

    if not house:
        return {"message": "Oops : propriété introuvable"}

    data = request.json

    house_type = data.get("house_type")
    house_rent = data.get("house_rent")
    house_guaranty = data.get("house_guaranty")
    house_month = data.get("house_month")
    house_number_room = data.get("house_number_room")
    house_address = data.get("house_address")

    house.vn_house_type = house_type
    house.vn_house_rent = house_rent
    house.vn_house_guaranty = house_guaranty
    house.vn_house_month = house_month
    house.vn_house_number_room = house_number_room
    house.vn_house_address = house_address

    house.save()

    return {"message": f"Location #{house.vn_house_id} mise à jour avec succès !"}


@api.delete("/houses/<string:house_uuid>/delete/")
@login_required
@jsonify_response
def delete_house(house_uuid):
    house = VNHouse.get_house(house_uuid)
    if house is not None:
        house.remove()
        return {
            "success": True,
            "message": f"Propriété #{house.vn_house_id} retirée avec succès.",
        }

    return {
        "success": False,
        "message": "Oups ! L'élément n'a pas été trouvé.",
    }


@api.get("/houses/<string:house_uuid>/payments/")
@login_required
@jsonify_response
def list_payments_for_house(house_uuid):

    house = VNHouse.get_house(house_uuid)

    if not house:
        return {"message": "Oops! propriété introuvable"}

    payments = []
    for payment in house.payments:
        payments.append(
            {
                "id": payment.vn_pay_id,
                "amount": payment.vn_pay_amount,
                "date": payment.vn_pay_date.isoformat(),
                "tenant": payment.tenant.vn_tenant_full_name,
            }
        )
    return {"payments": payments}
