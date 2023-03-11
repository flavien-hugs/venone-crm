from datetime import datetime
from datetime import timedelta

from flask import jsonify
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from src import db
from src.tenant import VNHouse
from src.tenant import VNHouseOwner
from src.tenant import VNTenant

from . import api


@api.get("/owners/")
@login_required
def get_all_houseowners():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = VNHouseOwner.get_owners_list().paginate(
        page=page, per_page=per_page, error_out=False
    )

    owners = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for("api.get_all_houseowners", page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for("api.get_all_houseowners", page=page + 1, _external=True)

    return jsonify(
        {
            "houseowners": [owner.to_json() for owner in owners],
            "prev": prev,
            "next": next,
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "user": current_user.to_json(),
        }
    )


@api.get("/owner/<string:owner_uuid>/")
@login_required
def get_houseowner(owner_uuid):
    owner = VNHouseOwner.get_owner(owner_uuid)
    return jsonify({"owner": owner.to_json()})


@api.delete("/owner/<string:owner_uuid>/delete/")
@login_required
def delete_houseowner(owner_uuid):
    owner = VNHouseOwner.get_owner(owner_uuid)
    if owner is not None:
        owner.disable()
        return jsonify(
            {
                "success": True,
                "message": f"Le compte du bailleur\
                    #{owner.vn_owner_id} a été supprimé avec succès.",
            }
        )
    return jsonify(
        {
            "success": False,
            "message": "Oups ! L'élément n'a pas été trouvé.",
        }
    )


@api.put("/owner/<string:owner_uuid>/update/")
@login_required
def update_houseowner(owner_uuid):
    owner = VNHouseOwner.get_owner(owner_uuid)

    if not owner:
        return jsonify({"message": "owner not found"}), 404

    data = request.get_json()
    fullname = data.get("fullname")
    addr_email = data.get("addr_email")
    card_number = data.get("card_number")
    location = data.get("location")
    profession = data.get("profession")
    parent_name = data.get("parent_name")
    phonenumber_one = data.get("phonenumber_one")
    phonenumber_two = data.get("phonenumber_two")

    owner.vn_fullname = fullname
    owner.vn_addr_email = addr_email
    owner.vn_cni_number = card_number
    owner.vn_location = location
    owner.vn_profession = profession
    owner.vn_parent_name = parent_name
    owner.vn_phonenumber_one = phonenumber_one
    owner.vn_phonenumber_two = phonenumber_two

    owner.save()

    return (
        jsonify(
            {
                "success": True,
                "message": f"Propriétaire #{owner.vn_owner_id} mise à jour avec succès !",
                "owner": owner.to_json(),
            }
        ),
        200,
    )


@api.post("/owner/<string:owner_uuid>/create_tenant/")
@login_required
def owner_create_tenant(owner_uuid):

    """
    Vue permettant la création d'un locataire
    pour un compte entreprise
    """

    owner = VNHouseOwner.get_owner(owner_uuid)

    if request.method == "POST":

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

        notice_period_days = 15
        lease_duration_days = 45

        notice_period = timedelta(days=notice_period_days)

        lease_end_date = (
            lease_start_date + timedelta(days=lease_duration_days) - notice_period
        )

        if hasattr(house, "vn_house_lease_end_date"):
            house.vn_house_lease_start_date = lease_end_date
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

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Nouveau locataire pour le propriétaire\
                        #{owner.vn_owner_id} ajouté avec succès !",
                }
            ),
            201,
        )

    return jsonify({"success": False, "message": "Erreur"})


@api.get("/owner/<string:owner_uuid>/houses/")
@login_required
def get_houseowner_houses(owner_uuid):
    owner = VNHouseOwner.get_owner(owner_uuid)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = owner.houses.paginate(page=page, per_page=per_page, error_out=False)

    houses = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for(
            "api.get_houseowner_houses", uuid=owner_uuid, page=page - 1, _external=True
        )
    next = None
    if pagination.has_next:
        next = url_for(
            "api.get_houseowner_houses", uuid=owner_uuid, page=page + 1, _external=True
        )

    return jsonify(
        {
            "houses": [house.to_json() for house in houses],
            "prev": prev,
            "next": next,
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
        }
    )


@api.route("/owner/<string:owner_uuid>/tenants/")
@login_required
def get_houseowner_tenants(owner_uuid):

    owner = VNHouseOwner.get_owner(owner_uuid)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = owner.tenants.paginate(page=page, per_page=per_page, error_out=False)

    tenants = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for(
            "api.get_houseowner_tenants", uuid=owner_uuid, page=page - 1, _external=True
        )
    next = None
    if pagination.has_next:
        next = url_for(
            "api.get_houseowner_tenants", uuid=owner_uuid, page=page + 1, _external=True
        )

    return jsonify(
        {
            "tenants": [tenant.to_json() for tenant in tenants],
            "prev": prev,
            "next": next,
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
        }
    )
