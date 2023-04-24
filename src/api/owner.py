from datetime import datetime
from datetime import timedelta

from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from src import db
from src.tenant import VNHouse
from src.tenant import VNHouseOwner
from src.tenant import VNTenant
from src.utils import jsonify_response

from . import api


@api.get("/owners/")
@login_required
@jsonify_response
def get_all_houseowners():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = current_user.houseowners.paginate(
        page=page, per_page=per_page, error_out=False
    )

    owners = pagination.items
    prev = (
        url_for("api.get_all_houseowners", page=page - 1, _external=True)
        if pagination.has_prev
        else None
    )
    next = (
        url_for("api.get_all_houseowners", page=page + 1, _external=True)
        if pagination.has_next
        else None
    )
    return {
        "houseowners": [owner.to_json() for owner in owners],
        "prev": prev,
        "next": next,
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "user": current_user.to_json(),
    }


@api.get("/owners/<string:owner_uuid>/")
@login_required
@jsonify_response
def get_houseowner(owner_uuid):
    owner = VNHouseOwner.get_owner(owner_uuid)
    return {
        "owner": owner.to_json(),
        "owner_houses": [h.to_json() for h in owner.houses],
        "owner_tenants": [t.to_json() for t in owner.tenants],
        "owner_payments": [p.to_json() for p in owner.payments],
    }


@api.delete("/owners/<string:owner_uuid>/delete/")
@login_required
@jsonify_response
def delete_houseowner(owner_uuid):
    owner = VNHouseOwner.get_owner(owner_uuid)
    if owner is not None:
        [h.remove() for h in owner.houses]
        [t.remove() for t in owner.tenants]
        owner.remove()
        return {
            "success": True,
            "message": f"Le compte du bailleur\
                #{owner.vn_owner_id} a été supprimé avec succès.",
        }

    return {
        "success": False,
        "message": "Oups ! L'élément n'a pas été trouvé.",
    }


@api.put("/owners/<string:owner_uuid>/update/")
@login_required
@jsonify_response
def update_houseowner(owner_uuid):
    owner = VNHouseOwner.get_owner(owner_uuid)

    if not owner:
        return {"message": "Oups ! L'élément n'a pas été trouvé."}

    data = request.get_json()
    fullname = data.get("fullname")
    addr_email = data.get("addr_email")
    card_number = data.get("card_number")
    location = data.get("location")
    profession = data.get("profession")
    parent_name = data.get("parent_name")
    phonenumber_one = data.get("phonenumber_one")
    phonenumber_two = data.get("phonenumber_two")
    percent = data.get("percent")

    owner.vn_fullname = fullname
    owner.vn_addr_email = addr_email
    owner.vn_cni_number = card_number
    owner.vn_location = location
    owner.vn_profession = profession
    owner.vn_parent_name = parent_name
    owner.vn_phonenumber_one = phonenumber_one
    owner.vn_phonenumber_two = phonenumber_two

    if (
        percent is not None
        and isinstance(percent, (int, float))
        and 0 <= percent <= 100
    ):
        owner.vn_owner_percent = percent
        owner.save()
        response_data = {
            "success": True,
            "message": f"Propriétaire #{owner.vn_owner_id} mis à jour avec succès.",
        }
    else:
        response_data = {
            "success": False,
            "message": "Valeur de pourcentage invalide.\
                Le pourcentage doit être un nombre entre 0 et 100.",
        }

    return response_data


@api.post("/owners/<string:owner_uuid>/create_tenant/")
@login_required
@jsonify_response
def owner_create_tenant(owner_uuid):

    """
    Vue permettant la création d'un locataire
    pour un compte entreprise
    """

    owner = VNHouseOwner.get_owner(owner_uuid)

    if not owner:
        return {
            "success": False,
            "message": "Oups ! L'élément n'a pas été trouvé",
        }

    house_data = request.json.get("house_data")
    tenant_data = request.json.get("tenant_data")

    house = VNHouse()

    house.vn_house_type = house_data.get("house_type")
    house.vn_house_rent = house_data.get("house_rent")
    house.vn_house_guaranty = house_data.get("house_guaranty")
    house.vn_house_month = house_data.get("house_month")
    house.vn_house_number_room = house_data.get("house_number_room")
    house.vn_house_address = house_data.get("house_address")
    lease_start_date = house_data.get("house_lease_start_date")

    house.vn_house_lease_start_date = (
        datetime.strptime(lease_start_date, "%Y-%m-%d").date()
        if lease_start_date
        else None
    )

    notice_period = timedelta(days=15)

    if lease_start_date:
        lease_end_date = (
            datetime.strptime(lease_start_date, "%Y-%m-%d")
            + timedelta(days=45)
            - notice_period
        ).date()

        if hasattr(house, "vn_house_lease_end_date"):
            house.vn_house_lease_end_date = lease_end_date
        else:
            raise AttributeError(
                "L'objet house doit avoir un attribut 'vn_house_lease_end_date'"
            )

        house.vn_user_id = current_user.id
        house.vn_owner_id = owner.id

        tenant = VNTenant()

        tenant.vn_fullname = tenant_data.get("fullname")
        tenant.vn_addr_email = tenant_data.get("addr_email")
        tenant.vn_cni_number = tenant_data.get("cni_number")
        tenant.vn_location = tenant_data.get("location")
        tenant.vn_profession = tenant_data.get("profession")
        tenant.vn_parent_name = tenant_data.get("parent_name")
        tenant.vn_phonenumber_one = tenant_data.get("phonenumber_one")
        tenant.vn_phonenumber_two = tenant_data.get("phonenumber_two")

        tenant.vn_user_id = current_user.id

        owner.houses.append(house)
        owner.tenants.append(tenant)
        house.tenants.append(tenant)

        db.session.add_all([house, tenant])
        db.session.commit()

        return {
            "success": True,
            "message": f"Nouveau locataire pour le propriétaire\
                #{owner.vn_owner_id} ajouté avec succès !",
        }


@api.get("/owners/<string:owner_uuid>/houses/")
@login_required
@jsonify_response
def get_houseowner_houses(owner_uuid):
    owner = VNHouseOwner.get_owner(owner_uuid)

    if not owner:
        return {
            "success": False,
            "message": "Oups ! L'élément n'a pas été trouvé !",
        }

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = owner.houses.paginate(page=page, per_page=per_page, error_out=False)

    houses = pagination.items

    prev = (
        url_for("api.get_houseowner_houses", page=page - 1, _external=True)
        if pagination.has_prev
        else None
    )
    next = (
        url_for("api.get_houseowner_houses", page=page + 1, _external=True)
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
    }


@api.get("/owners/<string:owner_uuid>/tenants/")
@login_required
@jsonify_response
def get_houseowner_tenants(owner_uuid):

    owner = VNHouseOwner.get_owner(owner_uuid)

    if not owner:
        return {
            "success": False,
            "message": "Oups ! L'élément n'a pas été trouvé !",
        }

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = owner.tenants.paginate(page=page, per_page=per_page, error_out=False)

    tenants = pagination.items
    prev = (
        url_for("api.get_houseowner_tenants", page=page - 1, _external=True)
        if pagination.has_prev
        else None
    )
    next = (
        url_for("api.get_houseowner_tenants", page=page + 1, _external=True)
        if pagination.has_next
        else None
    )

    return {
        "tenants": [tenant.to_json() for tenant in tenants],
        "prev": prev,
        "next": next,
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
    }
