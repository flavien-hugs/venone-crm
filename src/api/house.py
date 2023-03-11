from flask import jsonify
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from src.tenant import VNHouse

from . import api


@api.get("/houses/")
@login_required
def get_all_houses():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = VNHouse.get_houses_list().paginate(
        page=page, per_page=per_page, error_out=False
    )

    houses = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for("api.get_all_houses", page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for("api.get_all_houses", page=page + 1, _external=True)

    return jsonify(
        {
            "houses": [house.to_json() for house in houses],
            "prev": prev,
            "next": next,
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "user": current_user.to_json(),
        }
    )


@api.get("/house/<string:house_uuid>/")
@login_required
def get_house(house_uuid):
    house = VNHouse.get_house(house_uuid)
    return jsonify({"house": house.to_json()})


@api.put("/house/<string:house_uuid>/update/")
@login_required
def update_house(house_uuid):
    house = VNHouse.get_house(house_uuid)

    if not house:
        return jsonify({"message": "maison introuvable"}), 404

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

    return (
        jsonify(
            {
                "success": True,
                "message": f"Location #{house.vn_house_id} mise à jour avec succès !",
                "house": house.to_json(),
            }
        ),
        200,
    )


@api.delete("/house/<string:house_uuid>/delete/")
@login_required
def delete_house(house_uuid):
    house = VNHouse.get_house(house_uuid)
    if house is not None:
        house.disable()
        house.house_disable()
        return jsonify(
            {
                "success": True,
                "message": f"Propriété #{house.vn_house_id} retirée avec succès.",
            }
        )
    return jsonify(
        {
            "success": False,
            "message": "Oups ! L'élément n'a pas été trouvé.",
        }
    )


@api.route("/house/<string:house_uuid>/tenant/")
@login_required
def get_house_tenant(house_uuid):
    house = VNHouse.get_house(house_uuid)
    return jsonify({"house_tenant": house.vn_tenant.to_json()})
