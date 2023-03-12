from datetime import datetime
from datetime import timedelta

from flask import jsonify
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from src import db
from src.auth.models import VNUser
from src.mixins.decorators import agency_required
from src.mixins.decorators import owner_required
from src.tenant import VNHouse
from src.tenant import VNHouseOwner
from src.tenant import VNTenant

from . import api


@api.get("/users/")
@login_required
def get_all_users():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = VNUser.get_users_list().paginate(
        page=page, per_page=per_page, error_out=False
    )

    users = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for("api.get_all_users", page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for("api.get_all_users", page=page + 1, _external=True)

    return jsonify(
        {
            "users": [user.to_json() for user in users],
            "prev": prev,
            "next": next,
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
        }
    )


@api.get("/user/")
@login_required
def get_user():
    user = current_user.get_user_logged()
    return jsonify({"user": user.to_json()})


@api.get("/user/<string:user_uuid>/owners/")
@login_required
def get_user_owners(user_uuid):

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = current_user.houseowners.paginate(
        page=page, per_page=per_page, error_out=False
    )
    owners = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for("api.get_user_owners", page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for("api.get_user_owners", page=page + 1, _external=True)

    return jsonify(
        {
            "owners": [owner.to_json() for owner in owners],
            "prev": prev,
            "next": next,
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
        }
    )


@api.get("/user/<string:user_uuid>/tenants/")
@login_required
def get_user_tenants(user_uuid):

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = current_user.tenants.paginate(
        page=page, per_page=per_page, error_out=False
    )
    tenants = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for("api.get_user_tenants", page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for("api.get_user_tenants", page=page + 1, _external=True)

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


@api.get("/user/<string:user_uuid>/houses/")
@login_required
def get_user_houses(user_uuid):

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = current_user.houses.paginate(
        page=page, per_page=per_page, error_out=False
    )
    houses = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for("api.get_user_houses", page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for("api.get_user_houses", page=page + 1, _external=True)

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


@api.get("/user/<string:user_uuid>/payments/")
@login_required
def get_user_payments(user_uuid):

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = current_user.payments.paginate(
        page=page, per_page=per_page, error_out=False
    )
    payments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for("api.get_user_payments", page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for("api.get_user_payments", page=page + 1, _external=True)

    return jsonify(
        {
            "payments": [pay.to_json() for pay in payments],
            "prev": prev,
            "next": next,
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
        }
    )


@api.post("/owner/tenant_register/")
@login_required
@owner_required
def user_owner_register_tenant():

    if request.method == "POST":

        house_data = request.json.get("house_data")
        tenant_data = request.json.get("tenant_data")

        # Add house objects

        house = VNHouse()
        house.vn_house_type = house_data.get("house_type")
        house.vn_house_rent = house_data.get("house_rent")
        house.vn_house_month = house_data.get("house_month")
        house.vn_house_guaranty = house_data.get("house_guaranty")
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
            house.vn_house_lease_start_date
            + timedelta(days=lease_duration_days)
            - notice_period
        )

        if hasattr(house, "vn_house_lease_end_date"):
            house.vn_house_lease_end_date = lease_end_date
        else:
            raise AttributeError(
                "L'objet house doit avoir un attribut 'vn_house_lease_end_date'"
            )

        # Add tenant objects

        tenant = VNTenant()

        tenant.vn_fullname = tenant_data.get("fullname")
        tenant.vn_addr_email = tenant_data.get("addr_email")
        tenant.vn_cni_number = tenant_data.get("card_number")
        tenant.vn_location = tenant_data.get("location")
        tenant.vn_profession = tenant_data.get("profession")
        tenant.vn_parent_name = tenant_data.get("parent_name")
        tenant.vn_phonenumber_one = tenant_data.get("phonenumber_one")
        tenant.vn_phonenumber_two = tenant_data.get("phonenumber_two")

        current_user.houses.append(house)
        current_user.tenants.append(tenant)
        house.tenants.append(tenant)

        db.session.add_all([house, tenant])
        db.session.commit()

        return (
            jsonify({"success": True, "message": "Locataire ajouté avec succès !"}),
            201,
        )

    return jsonify({"success": False, "message": "Erreur"})


@api.post("/company/tenant_register/")
@login_required
@agency_required
def user_company_register_tenant():

    current_user_id = current_user.id

    if request.method == "POST":

        owner_data = request.json.get("owner_data")
        house_data = request.json.get("house_data")
        tenant_data = request.json.get("tenant_data")

        # Add owner objects
        owner = VNHouseOwner()
        owner.vn_gender = owner_data.get("gender")
        owner.vn_fullname = owner_data.get("fullname")
        owner.vn_addr_email = owner_data.get("addr_email")
        owner.vn_cni_number = owner_data.get("cni_number")
        owner.vn_location = owner_data.get("location")
        owner.vn_profession = owner_data.get("profession")
        owner.vn_parent_name = owner_data.get("parent_name")
        owner.vn_phonenumber_one = owner_data.get("phonenumber_one")
        owner.vn_phonenumber_two = owner_data.get("phonenumber_two")

        owner.vn_user_id = current_user_id

        # Add house objects

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
            house.vn_house_lease_start_date
            + timedelta(days=lease_duration_days)
            - notice_period
        )

        if hasattr(house, "vn_house_lease_end_date"):
            house.vn_house_lease_end_date = lease_end_date
        else:
            raise AttributeError(
                "L'objet house doit avoir un attribut 'vn_house_lease_end_date'"
            )

        house.vn_user_id = current_user_id
        house.vn_owner_id = owner.id

        # Add tenant objects

        tenant = VNTenant()

        tenant.vn_fullname = tenant_data.get("fullname")
        tenant.vn_addr_email = tenant_data.get("addr_email")
        tenant.vn_cni_number = tenant_data.get("card_number")
        tenant.vn_location = tenant_data.get("location")
        tenant.vn_profession = tenant_data.get("profession")
        tenant.vn_parent_name = tenant_data.get("parent_name")
        tenant.vn_phonenumber_one = tenant_data.get("phonenumber_one")
        tenant.vn_phonenumber_two = tenant_data.get("phonenumber_two")

        tenant.vn_user_id = current_user_id

        owner.houses.append(house)
        owner.tenants.append(tenant)
        house.tenants.append(tenant)

        db.session.add_all([owner, house, tenant])
        db.session.commit()

        return (
            jsonify({"success": True, "message": "Locataire ajouté avec succès !"}),
            201,
        )

    return jsonify({"success": False, "message": "Erreur"})
