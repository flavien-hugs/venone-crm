from datetime import datetime, timedelta
from http import HTTPStatus

from flask import abort, make_response, render_template, request
from flask_login import current_user, login_required

from src.api.schemas import houses
from src.core import get_house_service, get_user_service
from src.infrastructure.config.plugins import db
from src.infrastructure.persistence.models import House, HouseOwner, Tenant
from .__main__ import api_bp


def abort_if_house_doesnt_exist(uuid: str):
    house = db.session.get(House, uuid)
    if not house:
        abort(HTTPStatus.NOT_FOUND, f"Could not find house with ID {uuid}")

    if not current_user.is_administrator() and house.vn_user_id != current_user.id:
        abort(HTTPStatus.FORBIDDEN, "Access denied")

    return house


@api_bp.get("/houses/")
@login_required
def get_all_houses():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    user_service = get_user_service()
    query = user_service.get_houses_list(current_user.id)

    search_term = request.args.get("q", "", type=str)
    if search_term:
        query = query.join(HouseOwner, isouter=True).filter(
            db.or_(
                House.vn_house_type.ilike(f"%{search_term}%"),
                House.vn_house_address.ilike(f"%{search_term}%"),
                HouseOwner.vn_fullname.ilike(f"%{search_term}%"),
            )
        )

    houses_items = db.paginate(
        query,
        page=page,
        per_page=per_page,
        max_per_page=20,
        error_out=False,
        count=True,
    )

    return render_template(
        "tenant/partials/_houses_list.html",
        houses=houses_items,
        current_user=current_user,
    )


@api_bp.post("/houses/")
@login_required
def houses_register():
    data = request.form.to_dict()
    if not data:
        data = request.get_json() or {}

    fields = [
        "vn_house_type",
        "vn_house_rent",
        "vn_house_guaranty",
        "vn_house_month",
        "vn_house_number_room",
        "vn_house_address",
        "vn_owner_id",
    ]

    # Required fields validation
    required_fields = ["vn_house_type", "vn_house_rent", "vn_house_address"]
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return f'<div class="alert alert-danger">Champs obligatoires manquants : {", ".join(missing)}</div>'

    house = House()

    for field in fields:
        if field in data and data[field]:
            value = data[field]
            if field in ["vn_house_rent", "vn_house_guaranty"]:
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    value = 0.0
            elif field in ["vn_house_month", "vn_house_number_room", "vn_owner_id"]:
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    if field == "vn_owner_id":
                        value = None
                    else:
                        value = 1
            setattr(house, field, value)

    house.vn_house_is_open = False
    house.vn_user_id = current_user.id
    db.session.add(house)
    db.session.commit()

    response = make_response(
        '<div class="alert alert-success">Propriété ajoutée avec succès !</div>'
    )
    response.headers["HX-Trigger"] = "reload-house-list"
    return response


@api_bp.get("/houses/<string:uuid>/")
@login_required
def get_house(uuid: str) -> dict:
    house = abort_if_house_doesnt_exist(uuid)

    if not house:
        return {"error": "House not found"}

    # These are relationship accesses, still working on persistence model
    tnts = house.house_tenants
    pyms = house.house_payment

    return {
        "house": houses.house_schema.dump(house),
        "house_tenant": [houses.tenant_schema.dump(t) for t in tnts],
        "house_payment": [houses.payment_schema.dump(p) for p in pyms],
    }


@api_bp.patch("/houses/<string:uuid>/")
@login_required
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

    db.session.commit()
    response_data = {
        "success": True,
        "house": houses.house_schema.dump(house),
        "message": f"Location #{house.vn_house_id} mise à jour avec succès !",
    }
    return response_data


@api_bp.delete("/houses/<string:uuid>/")
@login_required
def delete_house(uuid: str) -> dict:
    house = abort_if_house_doesnt_exist(uuid)
    db.session.delete(house)
    db.session.commit()
    response_data = {
        "success": True,
        "house": houses.house_schema.dump(house),
        "message": f"Propriété #{house.vn_house_id} retirée avec succès.",
    }
    return response_data


@api_bp.get("/check-houses-country/")
@login_required
def get_houses_country():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 12, type=int)

    user_service = get_user_service()
    query = user_service.repository.get_houses_by_country(current_user.vn_country)
    pagination = db.paginate(query, page=page, per_page=per_page)

    return render_template(
        "dashboard/account/partials/_check_houses_list.html",
        houses=pagination.items,
        pagination=pagination,
    )


@api_bp.get("/available-houses/")
def get_houses_listing():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    house_service = get_house_service()
    query = house_service.house_repo.find_available_houses()
    pagination = db.paginate(query, page=page, per_page=per_page)

    return {
        "houses": [houses.house_schema.dump(house) for house in pagination.items],
    }


@api_bp.get("/available-houses/<string:uuid>/")
def get_house_info(uuid: str) -> dict:
    house_service = get_house_service()
    # Using find_by_house_id as a proxy for available houses here
    house_entity = house_service.house_repo.find_by_house_id(uuid)
    if not house_entity:
        abort(HTTPStatus.NOT_FOUND)

    # We need the model for the schema dump usually, but schemas could be updated later
    house_model = db.session.get(House, house_entity.id)
    return {"house": houses.house_schema.dump(house_model)}


@api_bp.post("/houses/assign-tenant/")
@login_required
def house_assign_tenant() -> str:
    # Assuming all data comes in a single form submission
    house_data = request.form
    tenant_data = request.form

    # Create House
    house = House(
        vn_house_type=house_data.get("vn_house_type"),
        vn_house_rent=float(house_data.get("vn_house_rent")),
        vn_house_guaranty=float(house_data.get("vn_house_guaranty")),
        vn_house_month=int(house_data.get("vn_house_month", 1)),
        vn_house_number_room=int(house_data.get("vn_house_number_room", 1)),
        vn_house_address=house_data.get("vn_house_address"),
        vn_house_is_open=True,
        vn_user_id=current_user.id,
    )

    lease_start_date_str = house_data.get("vn_house_lease_start_date")
    if lease_start_date_str:
        house.vn_house_lease_start_date = datetime.strptime(
            lease_start_date_str, "%Y-%m-%d"
        ).date()
        house.vn_house_lease_end_date = (
            house.vn_house_lease_start_date + timedelta(days=31) - timedelta(days=10)
        )

    db.session.add(house)
    db.session.flush()  # Flush to get house.id for tenant

    # Create Tenant
    tenant = Tenant(
        vn_fullname=tenant_data.get("vn_fullname"),
        vn_addr_email=tenant_data.get("vn_addr_email"),
        vn_cni_number=tenant_data.get("vn_cni_number"),
        vn_location=tenant_data.get("vn_location"),
        vn_profession=tenant_data.get("vn_profession"),
        vn_parent_name=tenant_data.get("vn_parent_name"),
        vn_phonenumber_one=tenant_data.get("vn_phonenumber_one"),
        vn_phonenumber_two=tenant_data.get("vn_phonenumber_two"),
        vn_house_id=house.id,
        vn_owner_id=house.vn_owner_id,  # Assuming owner_id is set on house or derived
        vn_user_id=current_user.id,
    )
    db.session.add(tenant)
    db.session.commit()

    return '<div class="alert alert-success" role="alert">Nouveau locataire ajouté avec succès !</div>'
