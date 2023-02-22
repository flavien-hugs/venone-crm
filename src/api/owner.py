from flask import jsonify
from flask import request
from flask import url_for
from flask_login import login_required
from src.tenant import VNHouseOwner

from . import api


@api.get("/owners/")
@login_required
def get_all_houseowners():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = VNHouseOwner.get_houseowners_list().paginate(
        page=page, per_page=per_page, error_out=False
    )

    houseowners = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for("api.get_all_houseowners", page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for("api.get_all_houseowners", page=page + 1, _external=True)

    return jsonify(
        {
            "houseowners": [owner.to_json() for owner in houseowners],
            "prev": prev,
            "next": next,
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
        }
    )


@api.get("/owner/<string:owner_uuid>/")
@login_required
def get_houseowner(owner_uuid):
    houseowner = VNHouseOwner.get_houseowner(owner_uuid)
    return jsonify(houseowner.to_json())


@api.delete("/owner/<string:owner_uuid>/delete/")
@login_required
def delete_houseowner(owner_uuid):
    owner = VNHouseOwner.get_houseowner(owner_uuid)
    if owner is not None:
        owner.disable()
        return jsonify(
            {
                "success": True,
                "message": f"Le compte du bailleur {owner} a été supprimé avec succès.",
            }
        )
    return jsonify(
        {
            "success": False,
            "message": f"L'élément avec l'id {owner_uuid} n'a pas été trouvé.",
        }
    )


@api.put("/owner/<string:owner_uuid>/update/")
@login_required
def update_houseowner(owner_uuid):
    owner = VNHouseOwner.get_houseowner(owner_uuid)

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
                "message": f"Owner {owner.vn_owner_id} updated successfully",
                "owner": owner.to_json(),
            }
        ),
        200,
    )


@api.get("/owner/<string:owner_uuid>/houses/")
@login_required
def get_houseowner_houses(owner_uuid):
    houseowner = VNHouseOwner.get_houseowner(owner_uuid)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = houseowner.houses.paginate(
        page=page, per_page=per_page, error_out=False
    )

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
    houseowner = VNHouseOwner.get_houseowner(owner_uuid)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = houseowner.tenants.paginate(
        page=page, per_page=per_page, error_out=False
    )

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
