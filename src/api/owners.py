from datetime import datetime, timedelta
from http import HTTPStatus

from flask import abort, make_response, render_template, request
from flask_login import current_user, login_required

from src.api.schemas import owners
from src.api.shared.helpers import jsonify_response
from src.core import get_user_service
from src.infrastructure.config.plugins import cache, db
from src.infrastructure.persistence.models import House, HouseOwner, Tenant
from .__main__ import api_bp


@api_bp.post("/owners/")
@login_required
def owners_register():
    data = request.form.to_dict()
    if not data:
        data = request.get_json() or {}

    fields = [
        "vn_fullname",
        "vn_addr_email",
        "vn_cni_number",
        "vn_location",
        "vn_profession",
        "vn_parent_name",
        "vn_phonenumber_one",
        "vn_phonenumber_two",
        "vn_owner_percent",
    ]

    missing_fields = [
        f for f in ["vn_fullname", "vn_phonenumber_one"] if not data.get(f)
    ]
    if missing_fields:
        return f'<div class="alert alert-danger">Les champs suivants sont obligatoires : {", ".join(missing_fields)}</div>'

    owner = HouseOwner()
    for field in fields:
        if field in data and data[field]:
            value = data[field]
            if field == "vn_owner_percent":
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    value = 0.0
            setattr(owner, field, value)

    owner.vn_user_id = current_user.id
    db.session.add(owner)
    db.session.commit()

    response = make_response(
        f'<div class="alert alert-success">Le bailleur {owner.vn_fullname} a été enregistré avec succès !</div>'
    )
    response.headers["HX-Trigger"] = "reload-owner-list"
    return response


def abort_if_owner_doesnt_exist(uuid: str):
    owner = HouseOwner.query.filter_by(uuid=uuid).first()
    if not owner:
        abort(HTTPStatus.NOT_FOUND, f"Could not find owner with ID {uuid}")

    if not current_user.is_administrator() and owner.vn_user_id != current_user.id:
        abort(HTTPStatus.FORBIDDEN, "Access denied")

    return owner


@api_bp.get("/owners/")
@login_required
def get_all_owners():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    user_service = get_user_service()
    query = user_service.get_owners_list(current_user.id)

    search_term = request.args.get("q", "", type=str)
    if search_term:
        query = query.filter(
            db.or_(
                HouseOwner.vn_fullname.ilike(f"%{search_term}%"),
                HouseOwner.vn_addr_email.ilike(f"%{search_term}%"),
                HouseOwner.vn_phonenumber_one.ilike(f"%{search_term}%"),
                HouseOwner.vn_cni_number.ilike(f"%{search_term}%"),
                HouseOwner.vn_location.ilike(f"%{search_term}%"),
            )
        )

    owners_items = db.paginate(
        query,
        page=page,
        per_page=per_page,
        max_per_page=20,
        error_out=False,
        count=True,
    )

    return render_template(
        "tenant/partials/_owner_list.html",
        owners=owners_items,
        current_user=current_user,
    )


@api_bp.get("/owners/<string:uuid>/")
@login_required
@jsonify_response
@cache.cached(timeout=500)
def get_houseowner(uuid: str) -> dict:
    owner = abort_if_owner_doesnt_exist(uuid)
    return {"owner": owners.owner_schema.dump(owner)}


@api_bp.delete("/owners/<string:uuid>/")
@login_required
@jsonify_response
def delete_houseowner(uuid: str) -> dict:
    owner = abort_if_owner_doesnt_exist(uuid)
    [db.session.delete(h) for h in owner.owner_houses]
    [db.session.delete(t) for t in owner.owner_tenants]
    db.session.delete(owner)
    db.session.commit()
    return {
        "success": True,
        "message": f"Le compte du bailleur #{owner.vn_owner_id} a été supprimé avec succès.",
    }


@api_bp.patch("/owners/<string:uuid>/")
@login_required
@jsonify_response
def update_houseowner(uuid: str) -> dict:
    owner = abort_if_owner_doesnt_exist(uuid)

    data = request.get_json()
    vn_owner_percent = data.get("vn_owner_percent")
    if (
        vn_owner_percent is not None
        and isinstance(vn_owner_percent, (int, float))
        and 0 <= vn_owner_percent <= 100
    ):
        owner.vn_owner_percent = vn_owner_percent

    fields = [
        "vn_fullname",
        "vn_addr_email",
        "vn_cni_number",
        "vn_location",
        "vn_profession",
        "vn_parent_name",
        "vn_phonenumber_one",
        "vn_phonenumber_two",
    ]
    for field in fields:
        if field in data:
            setattr(owner, field, data[field])

    db.session.commit()

    if vn_owner_percent is not None:
        response_data = {
            "success": True,
            "message": f"Propriétaire #{owner.vn_owner_id} mis à jour avec succès.",
        }
    else:
        response_data = {
            "message": "Valeur de pourcentage invalide. Le pourcentage doit être un nombre entre 0 et 100.",
        }

    return response_data


@api_bp.post("/owners/<string:uuid>/create-tenant/")
@login_required
@jsonify_response
def owner_create_tenant(uuid: str) -> dict:
    owner = abort_if_owner_doesnt_exist(uuid)

    house_data = request.json.get("house_data")

    house = House()
    fields = [
        "vn_house_type",
        "vn_house_rent",
        "vn_house_guaranty",
        "vn_house_month",
        "vn_house_number_room",
        "vn_house_address",
    ]
    lease_start_date = house_data.get("vn_house_lease_start_date")

    for field in fields:
        if field in house_data:
            setattr(house, field, house_data[field])

    if lease_start_date:
        lease_start = datetime.strptime(lease_start_date, "%Y-%m-%d").date()
        lease_end = lease_start + timedelta(days=31) - timedelta(days=10)
        house.vn_house_lease_start_date = lease_start
        house.vn_house_lease_end_date = lease_end

        house.vn_user_id = current_user.id
        house.vn_owner_id = owner.id
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
    tenant = Tenant()
    for field in tenant_fields:
        if field in tenant_data:
            setattr(tenant, field, tenant_data[field])

    tenant.vn_user_id = current_user.id
    owner.owner_houses.append(house)
    owner.owner_tenants.append(tenant)
    house.house_tenants.append(tenant)

    db.session.add_all([house, tenant])
    db.session.commit()

    response_data = {
        "success": True,
        "message": f"Nouveau locataire pour le propriétaire #{owner.vn_owner_id} ajouté avec succès !",
    }

    return response_data
