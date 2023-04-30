import re
from datetime import datetime
from datetime import timedelta

from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from src import db
from src.auth.models import VNUser
from src.mixins.decorators import admin_required
from src.mixins.decorators import agency_required
from src.mixins.decorators import owner_required
from src.tenant import VNHouse
from src.tenant import VNHouseOwner
from src.tenant import VNTenant
from src.utils import jsonify_response

from . import api

# from src.schemas import user_schema
# from src.schemas import users_schema


@api.get("/users/")
@login_required
def get_user():
    user = current_user.get_user_logged()
    if not user:
        return {"message": "Oups ! L'élément n'a pas été trouvé."}
    return {"user": user.to_json()}


@api.get("/customers/")
@login_required
@jsonify_response
@admin_required
def get_all_users():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = VNUser.get_users_list().paginate(
        page=page, per_page=per_page, error_out=False
    )

    users = pagination.items
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
        "users": [user.to_json() for user in users],
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
        "companies": [user.to_json() for user in companies],
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
        "lessors": [user.to_json() for user in lessors],
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
def user_owner_register_tenant():

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
def user_company_register_tenant():

    current_user_id = current_user.id

    if not current_user_id:
        return {
            "message": "Oups ! L'élément n'a pas été trouvé !",
        }

    owner_data = request.json.get("owner_data")
    house_data = request.json.get("house_data")
    tenant_data = request.json.get("tenant_data")

    # add owner objects
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

    # add house objects
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

    # add tenant objects
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

    return {
        "success": True,
        "message": "Locataire ajouté avec succès !",
    }


@api.post("/houses-register/")
@login_required
@jsonify_response
def user_owner_register_house():

    if not current_user:
        return {
            "message": "Oups ! L'élément n'a pas été trouvé !",
        }

    house_data = request.json.get("house_data")
    house = VNHouse()
    house.vn_house_type = house_data.get("house_type")
    house.vn_house_rent = house_data.get("house_rent")
    house.vn_house_month = house_data.get("house_month")
    house.vn_house_guaranty = house_data.get("house_guaranty")
    house.vn_house_number_room = house_data.get("house_number_room")
    house.vn_house_address = house_data.get("house_address")
    house.vn_house_is_open = False

    current_user.houses.append(house)
    house.save()

    return {
        "success": True,
        "message": "Propriété ajoutée avec succès !",
    }


def owners_to_json(owner):
    return {
        "owner_uuid": owner.uuid,
        "gender": owner.vn_gender,
        "fullname": owner.vn_fullname,
        "addr_email": owner.vn_addr_email,
        "profession": owner.vn_profession,
        "parent_name": owner.vn_parent_name,
        "card_number": owner.vn_cni_number,
        "location": owner.vn_location,
        "percent": owner.vn_owner_percent,
        "phonenumber_one": owner.vn_phonenumber_one,
        "phonenumber_two": owner.vn_phonenumber_two,
        "is_activated": owner.vn_activated,
        "created_at": owner.vn_created_at.strftime("%d-%m-%Y"),
    }


def user_to_json(user):
    return {
        "user_id": user.uuid,
        "fullname": user.vn_fullname,
        "profession": user.vn_profession,
        "parent_name": user.vn_parent_name,
        "phonenumber_one": user.vn_phonenumber_one,
        "phonenumber_two": user.vn_phonenumber_two,
        "cni_number": user.vn_cni_number,
        "location": user.vn_location,
        "country": user.vn_country,
        "agencie_name": user.vn_agencie_name,
        "business_number": user.vn_business_number,
        "devise": user.vn_device,
        "find_us": user.vn_find_us,
        "ip_address": user.vn_ip_address,
        "is_company": user.vn_company,
        "is_owner": user.vn_house_owner,
        "is_activated": user.vn_activated,
        "last_seen": user.vn_last_seen,
        "created_at": user.vn_created_at.strftime("%d-%m-%Y"),
        "tenants_count": user.tenants.count(),
        "houses_count": user.houses.count(),
        "owners_count": user.houseowners.count(),
        "owners_list": [owners_to_json(owner) for owner in user.houseowners.all()],
    }


@api.post("/login/")
@jsonify_response
def login():

    data = request.get_json()
    email_or_phone = data.get("email_or_phone", None)
    passowrd = data.get("vn_password", None)

    user = VNUser.query.filter(
        (VNUser.vn_addr_email == email_or_phone)
        | (VNUser.vn_phonenumber_one == email_or_phone)
    ).first()

    if user and user.verify_password(passowrd) and user.vn_activated:
        return {
            "success": True,
            "user": user_to_json(user),
            "message": f"Hello, bienvenue sur votre tableau de bord {email_or_phone}",
        }

    return {
        "success": False,
        "message": "L'utilisateur n'existe pas ou le compte à été désactivé !\
            Veuillez contacter l'administrateur système.",
    }


@api.post("/register/")
@jsonify_response
def register():

    data = request.get_json()
    addr_email = data.get("vn_addr_email", None)

    if not data.get("addr_email"):
        return {"message": "The e-mail address cannot be empty."}

    if not re.match(r"[^@]+@[^@]+\.[^@]+", addr_email):
        return {"message": "The email address is invalid."}

    if VNUser.query.filter_by(vn_addr_email=addr_email).first():
        return {"message": f"This address email '{addr_email}!r' is taken !"}

    fullname = data.get("vn_fullname", None)
    phonenumber_one = data.get("vn_phonenumber_one", None)
    cni_number = data.get("vn_cni_number", None)
    country = data.get("vn_country", None)
    password = data.get("vn_password", None)
    is_company = data.get("vn_company", None)
    is_house_owner = data.get("vn_house_owner", None)

    new_user = VNUser(
        vn_fullname=fullname,
        vn_addr_email=addr_email.lower(),
        vn_phonenumber_one=phonenumber_one,
        vn_cni_number=cni_number,
        vn_country=country,
        vn_house_owner=is_house_owner,
        vn_company=is_company,
    )
    new_user.set_password(password)
    new_user.vn_activated = True
    new_user.save()
    return {
        "success": True,
        "user": user_to_json(new_user),
        "message": "account successfully created!",
    }


"""
@api.get("/users-all/")
def users_all():
    all_users = VNUser.query.all()
    return users_schema.dump(all_users)


@api.get("/users/<id>")
def user_detail(id):
    user = VNUser.query.get(id)
    return user_schema.dump(user)
"""
