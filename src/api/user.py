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
from src.mixins.decorators import admin_required
from src.mixins.decorators import agency_required
from src.mixins.decorators import owner_required
from src.schemas import users
from src.tenant import VNHouse
from src.tenant import VNHouseOwner
from src.tenant import VNTenant
from src.utils import jsonify_response

from . import api


def abort_if_user_doesnt_exist(uuid: str):
    user = VNUser.find_by_uuid(uuid)
    if not user:
        abort(HTTPStatus.NOT_FOUND, f"Could not find user with ID {uuid}")
    return user


@api.get("/users/")
@login_required
def get_user():
    user = current_user.get_user_logged()
    if not user:
        return {"message": "Oups ! L'élément n'a pas été trouvé."}
    return {"user": users.user_schema.dump(user)}


@api.get("/customers/")
@login_required
@admin_required
@jsonify_response
def get_all_users():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = VNUser.get_users_list().paginate(
        page=page, per_page=per_page, error_out=False
    )

    users_items = pagination.items
    prev = None
    prev = (
        url_for("api.get_all_users", page=page - 1, _external=True)
        if pagination.has_prev
        else None
    )
    next = (
        url_for("api.get_all_users", page=page + 1, _external=True)
        if pagination.has_next
        else None
    )

    return {
        "users": users.users_schema.dump(users_items),
        "prev": prev,
        "next": next,
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
    }


@api.get("/companies/")
@login_required
@admin_required
@jsonify_response
def get_all_companies():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = VNUser.get_companies_list().paginate(
        page=page, per_page=per_page, error_out=False
    )

    companies = pagination.items
    prev = (
        url_for("api.get_all_companies", page=page - 1, _external=True)
        if pagination.has_prev
        else None
    )
    next = (
        url_for("api.get_all_companies", page=page + 1, _external=True)
        if pagination.has_next
        else None
    )

    return {
        "companies": users.users_schema.dump(companies),
        "prev": prev,
        "next": next,
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
    }


@api.get("/lessors/")
@login_required
@admin_required
@jsonify_response
def get_all_lessors():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = VNUser.get_lessors_list().paginate(
        page=page, per_page=per_page, error_out=False
    )

    lessors = pagination.items
    prev = (
        url_for("api.get_all_lessors", page=page - 1, _external=True)
        if pagination.has_prev
        else None
    )
    next = (
        url_for("api.get_all_lessors", page=page + 1, _external=True)
        if pagination.has_next
        else None
    )

    return {
        "lessors": users.users_schema.dump(lessors),
        "prev": prev,
        "next": next,
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
    }


@api.post("/owners/tenant-register/")
@login_required
@owner_required
@jsonify_response
def owner_register_tenant():

    if not current_user:
        return {
            "message": "Oups ! L'élément n'a pas été trouvé !",
        }

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

    return {
        "success": True,
        "message": "Locataire ajouté avec succès !",
    }


@api.post("/companies/tenant-register/")
@login_required
@agency_required
@jsonify_response
def company_register_tenant():

    user = abort_if_user_doesnt_exist(current_user.uuid)

    owner_data = request.json.get("owner_data")
    house_data = request.json.get("house_data")
    tenant_data = request.json.get("tenant_data")

    # add owner
    owner = VNHouseOwner()
    owner_percent = owner_data.get("vn_owner_percent")
    if (
        owner_percent is not None
        and isinstance(owner_percent, (int, float))
        and 0 <= owner_percent <= 100
    ):
        owner.vn_owner_percent = owner_percent

    owner_fields = [
        "vn_fullname",
        "vn_addr_email",
        "vn_cni_number",
        "vn_location",
        "vn_profession",
        "vn_parent_name",
        "vn_phonenumber_one",
        "vn_phonenumber_two",
    ]
    for field in owner_fields:
        if field in owner_data:
            setattr(owner, field, owner_data[field])

    owner.vn_user_id = user.id

    # add house
    house = VNHouse()
    house_fields = [
        "vn_house_type",
        "vn_house_rent",
        "vn_house_guaranty",
        "vn_house_month",
        "vn_house_number_room",
        "vn_house_address",
    ]

    lease_start_date = house_data.get("vn_house_lease_end_date")
    if lease_start_date:
        lease_start = datetime.strptime(lease_start_date, "%Y-%m-%d").date()
        lease_end = lease_start + timedelta(days=31) - timedelta(days=10)
        house.vn_house_lease_start_date = lease_start

        if not hasattr(house, "vn_house_lease_end_date"):
            raise AttributeError(
                "L'objet house doit avoir un attribut 'vn_house_lease_end_date'"
            )
        house.vn_house_lease_end_date = lease_end

    for field in house_fields:
        if field in house_data:
            setattr(house, field, house_data[field])

    house.vn_user_id = user.id
    house.owner = owner

    # add tenant
    tenant = VNTenant()
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
    for field in tenant_fields:
        if field in tenant_data:
            setattr(tenant, field, tenant_data[field])

    tenant.vn_user_id = user.id
    tenant.owner = owner
    tenant.house = house

    db.session.add_all([owner, house, tenant])
    db.session.commit()

    return {
        "success": True,
        "message": "Nouveau locataire ajouté avec succès !",
    }


@api.post("/login/")
@jsonify_response
def login():

    data = request.get_json()
    email_or_phone = data.get("email_or_phone", None)
    passowrd = data.get("vn_password", None)

    user = VNUser.find_by_email_and_phone(email_or_phone)

    if user and user.verify_password(passowrd) and user.vn_activated:
        return {
            "success": True,
            "user": users.user_schema.dump(user),
            "message": f"Hello, bienvenue sur votre tableau de bord {email_or_phone}",
        }

    return {
        "success": False,
        "message": "L'utilisateur n'existe pas ou le compte à été désactivé !\
            Veuillez contacter l'administrateur système.",
    }
