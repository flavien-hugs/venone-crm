from datetime import datetime
from datetime import timedelta

from flask import jsonify
from flask import make_response
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from src import db
from src.tenant import VNHouse
from src.tenant import VNTenant

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

    return make_response(
        jsonify(
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
    )


@api.get("/house/<string:house_uuid>/")
@login_required
def get_house(house_uuid):

    house = VNHouse.get_house(house_uuid)

    if not house:
        return make_response(jsonify({"error": "House not found"}), 404)

    tenants = house.tenants(page=request.args.get("page", 1, type=int))
    payments = house.payments(page=request.args.get("page", 1, type=int))

    return make_response(
        jsonify(
            {
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
        )
    )


@api.patch("/house/<string:house_uuid>/house_assign_tenant/")
@login_required
def house_assign_tenant(house_uuid):

    """
    Vue permettant d'assigner une propriété disponible
    à un locataire
    """

    house = VNHouse.get_house(house_uuid)

    if not house:
        return make_response(jsonify({"message": "maison introuvable"})), 404

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

    return make_response(
        jsonify(
            {
                "success": True,
                "message": "Nouveau locataire ajouté avec succès",
            }
        ),
        201,
    )

    return make_response(
        jsonify({"success": False, "message": "Une erreur s'est lors de l'ajout !"})
    )


@api.put("/house/<string:house_uuid>/update/")
@login_required
def update_house(house_uuid):
    house = VNHouse.get_house(house_uuid)

    if not house:
        return make_response(jsonify({"message": "Oops : propriété introuvable"})), 404

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

    return make_response(
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
        house.remove()
        return make_response(
            jsonify(
                {
                    "success": True,
                    "message": f"Propriété #{house.vn_house_id} retirée avec succès.",
                }
            )
        )

    return make_response(
        jsonify(
            {
                "success": False,
                "message": "Oups ! L'élément n'a pas été trouvé.",
            }
        )
    )


@api.get("/house/<string:house_uuid>/payments/")
@login_required
def list_payments_for_house(house_uuid):

    house = VNHouse.get_house(house_uuid)

    if not house:
        return jsonify({"message": "Oops! propriété introuvable"}), 404

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
    return make_response(jsonify({"payments": payments})), 200
