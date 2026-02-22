from datetime import datetime, timedelta
from http import HTTPStatus

from flask import abort, request, url_for
from flask_login import current_user, login_required

from src.exts import cache, db
from src.schemas import owners, users
from src.tenant import VNHouse, VNHouseOwner, VNTenant
from src.utils import jsonify_response

from . import api


def abort_if_owner_doesnt_exist(uuid: str):
    user = VNHouseOwner.find_by_uuid(uuid)
    if not user:
        abort(HTTPStatus.NOT_FOUND, f"Could not find owner with ID {uuid}")
    return user


@api.get("/owners/")
@login_required
@jsonify_response
def get_all_owners():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = VNHouseOwner.get_owners_list()
    owners_items = db.paginate(
        query, page=page, per_page=per_page, max_per_page=20, error_out=True, count=True
    )
    owner_ids = owners_items.items

    prev = (
        url_for("api.get_all_owners", page=page - 1, _external=True)
        if owners_items.has_prev
        else None
    )
    next = (
        url_for("api.get_all_owners", page=page + 1, _external=True)
        if owners_items.has_next
        else None
    )
    return {
        "owners": owners.owners_schema.dump(owner_ids),
        "user": users.user_schema.dump(current_user),
        "prev": prev,
        "next": next,
        "page": page,
        "per_page": per_page,
        "total": owners_items.total,
    }


@api.get("/owners/<string:uuid>/")
@login_required
@jsonify_response
@cache.cached(timeout=500)
def get_houseowner(uuid: str) -> dict:
    owner = abort_if_owner_doesnt_exist(uuid)
    return {"owner": owners.owner_schema.dump(owner)}


@api.delete("/owners/<string:uuid>/")
@login_required
@jsonify_response
def delete_houseowner(uuid: str) -> dict:
    owner = abort_if_owner_doesnt_exist(uuid)
    [h.remove() for h in owner.houses]
    [t.remove() for t in owner.tenants]
    owner.remove()
    return {
        "success": True,
        "message": f"Le compte du bailleur\
        #{owner.vn_owner_id} a été supprimé avec succès.",
    }


@api.patch("/owners/<string:uuid>/")
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
    owner.save()

    if vn_owner_percent is not None:
        response_data = {
            "success": True,
            "message": f"Propriétaire #{owner.vn_owner_id} mis à jour avec succès.",
        }
    else:
        response_data = {
            "message": "Valeur de pourcentage invalide.\
                Le pourcentage doit être un nombre entre 0 et 100.",
        }

    return response_data


@api.post("/owners/<string:uuid>/create-tenant/")
@login_required
@jsonify_response
def owner_create_tenant(uuid: str) -> dict:
    owner = abort_if_owner_doesnt_exist(uuid)

    house_data = request.json.get("house_data")

    house = VNHouse()
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
        else:
            response_data = {
                "success": False,
                "message": f"Le champ {field} est manquant.",
            }

    if lease_start_date:
        lease_start = datetime.strptime(lease_start_date, "%Y-%m-%d").date()
        lease_end = lease_start + timedelta(days=31) - timedelta(days=10)
        house.vn_house_lease_start_date = lease_start

        if not hasattr(house, "vn_house_lease_end_date"):
            raise AttributeError(
                "L'objet house doit avoir un attribut 'vn_house_lease_end_date'"
            )
        house.vn_house_lease_end_date = lease_end

        house.vn_user_id = current_user.id
        house.vn_owner_id = owner.id

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

    tenant.vn_user_id = current_user.id
    owner.owner_houses.append(house)
    owner.owner_tenants.append(tenant)
    house.house_tenants.append(tenant)

    db.session.add_all([house, tenant])
    db.session.commit()

    response_data = {
        "success": True,
        "message": f"Nouveau locataire pour le propriétaire\
            #{owner.vn_owner_id} ajouté avec succès !",
    }

    return response_data
