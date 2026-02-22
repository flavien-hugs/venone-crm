from datetime import datetime
from datetime import timedelta
from http import HTTPStatus

from flask import abort
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from src.auth.models import VNUser
from src.exts import cache
from src.exts import db
from src.schemas import houses
from src.schemas import users
from src.tenant import VNHouse
from src.tenant import VNTenant
from src.utils import jsonify_response

from . import api
from .user import abort_if_user_doesnt_exist


def abort_if_house_doesnt_exist(uuid: str):
    user = VNHouse.find_by_uuid(uuid)
    if not user:
        abort(HTTPStatus.NOT_FOUND, f"Could not find house with ID {uuid}")
    return user


@api.get("/houses/")
@login_required
@jsonify_response
def get_all_houses():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = VNHouse.get_houses_list()
    houses_items = db.paginate(
        query, page=page, per_page=per_page, max_per_page=20, error_out=True, count=True
    )
    house_ids = houses_items.items

    prev = (
        url_for("api.get_all_houses", page=page - 1, _external=True)
        if houses_items.has_prev
        else None
    )
    next = (
        url_for("api.get_all_houses", page=page + 1, _external=True)
        if houses_items.has_next
        else None
    )

    return {
        "houses": houses.houses_schema.dump(house_ids),
        "user": users.user_schema.dump(current_user),
        "prev": prev,
        "next": next,
        "page": page,
        "per_page": per_page,
        "total": houses_items.total,
    }


@api.post("/houses/")
@login_required
@jsonify_response
def houses_register():
    create_house_data = request.json.get("create_house_data")

    fields = [
        "vn_house_type",
        "vn_house_rent",
        "vn_house_guaranty",
        "vn_house_month",
        "vn_house_number_room",
        "vn_house_address",
    ]
    house = VNHouse()

    for field in fields:
        if field in create_house_data:
            setattr(house, field, create_house_data[field])
        else:
            response_data = {
                "success": False,
                "message": f"Le champ {field} est manquant.",
            }

    house.vn_house_is_open = False
    user = abort_if_user_doesnt_exist(current_user.uuid)

    user.houses.append(house)
    house.save()

    response_data = {
        "success": True,
        "message": "Propriété ajoutée avec succès !",
    }

    return response_data


@api.get("/houses/<string:uuid>/")
@login_required
@jsonify_response
@cache.cached(timeout=500)
def get_house(uuid: str) -> dict:
    house = abort_if_house_doesnt_exist(uuid)

    if not house:
        return {"error": "House not found"}

    tnts = house.tenants(page=request.args.get("page", 1, type=int))
    pyms = house.payments(page=request.args.get("page", 1, type=int))

    return {
        "house": houses.house_schema.dump(house),
        "house_tenant": [houses.tenant_schema.dump(t) for t in tnts.items],
        "house_tenants_pagination": {
            "page": tnts.page,
            "per_page": tnts.per_page,
            "total": tnts.total,
            "pages": tnts.pages,
        },
        "house_payment": [houses.payment_schema.dump(p) for p in pyms.items],
        "house_payments_pagination": {
            "page": pyms.page,
            "per_page": pyms.per_page,
            "total": pyms.total,
            "pages": pyms.pages,
        },
    }


@api.patch("/houses/<string:uuid>/")
@login_required
@jsonify_response
def update_house(uuid: str) -> dict:
    house = abort_if_house_doesnt_exist(uuid)

    data = request.json

    fields = [
        "vn_house_type",
        "vn_house_rent",
        "vn_house_guaranty",
        "vn_house_month",
        "vn_house_number_room",
        "vn_house_address",
    ]
    for field in fields:
        if field in data:
            setattr(house, field, data[field])
    house.save()
    response_data = {
        "success": True,
        "house": houses.house_schema.dump(house),
        "message": f"Location #{house.vn_house_id} mise à jour avec succès !",
    }
    return response_data


@api.delete("/houses/<string:uuid>/")
@login_required
@jsonify_response
def delete_house(uuid: str) -> dict:
    house = abort_if_house_doesnt_exist(uuid)
    house.remove()
    response_data = {
        "success": True,
        "house": houses.house_schema.dump(house),
        "message": f"Propriété #{house.vn_house_id} retirée avec succès.",
    }
    return response_data


@api.get("/check-houses-country/")
@login_required
@jsonify_response
@cache.cached(timeout=500)
def get_houses_country():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 12, type=int)
    pagination, houses_all = VNUser.get_houses_by_country(page, per_page)

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
        "houses": houses.houses_schema.dump(houses_all),
        "prev": prev,
        "next": next,
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
    }


@api.get("/available-houses/")
@jsonify_response
@cache.cached(timeout=500)
def get_houses_listing():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    houses_select = VNHouse.get_houses_list()
    pagination = db.paginate(houses_select, page=page, per_page=per_page)
    return {
        "houses": [houses.house_schema.dump(house) for house in pagination.items],
    }


@api.get("/available-houses/<string:uuid>/")
@jsonify_response
@cache.cached(timeout=500)
def get_house_info(uuid: str) -> dict:
    house = VNHouse.get_available_houses(uuid)
    house = abort_if_house_doesnt_exist(house)
    return {"house": houses.house_schema.dump(house)}


@api.patch("/houses/<string:uuid>/house-assign-tenant/")
@login_required
@jsonify_response
def house_assign_tenant(uuid: str) -> dict:
    house = abort_if_house_doesnt_exist(uuid)

    house_data = request.json.get("house_data")
    lease_start_date = house_data.get("vn_house_lease_start_date")

    if lease_start_date:
        lease_start = datetime.strptime(lease_start_date, "%Y-%m-%d").date()
        lease_end = lease_start + timedelta(days=31) - timedelta(days=10)
        house.vn_house_lease_start_date = lease_start

        if not hasattr(house, "vn_house_lease_end_date"):
            raise AttributeError(
                "L'objet house doit avoir un attribut 'vn_house_lease_end_date'"
            )
        house.vn_house_lease_end_date = lease_end

    house_fields = [
        "vn_house_type",
        "vn_house_rent",
        "vn_house_guaranty",
        "vn_house_month",
        "vn_house_number_room",
        "vn_house_address",
    ]

    for field in house_fields:
        if field in house_data:
            setattr(house, field, house_data[field])
    house.vn_house_is_open = True

    tenant_data = request.json.get("tenant_data")
    tenant_fields = [
        "vn_fullname",
        "vn_addr_email",
        "vn_cni_number",
        "vn_location",
        "vn_profession",
        "vn_parent_name",
        "vn_phonenumber_one",
        "vn_phonenumber_two",
    ]
    tenant = VNTenant()
    for field in tenant_fields:
        if field in tenant_data:
            setattr(tenant, field, tenant_data[field])

    house.house_tenants.append(tenant)
    tenant.vn_owner_id = house.vn_owner_id
    tenant.vn_user_id = current_user.id

    db.session.add_all([house, tenant])
    db.session.commit()

    return {
        "success": True,
        "message": "Nouveau locataire ajouté avec succès",
    }
