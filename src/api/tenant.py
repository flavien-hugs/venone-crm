from http import HTTPStatus

from flask import abort, request, url_for
from flask_login import current_user, login_required

from src.exts import cache, db
from src.schemas import houses, users
from src.tenant import VNTenant
from src.utils import jsonify_response

from . import api


def abort_if_tenant_doesnt_exist(uuid: str):
    tenant = VNTenant.find_by_uuid(uuid)
    if not tenant:
        abort(HTTPStatus.NOT_FOUND, f"Could not find user with ID {uuid}")
    return tenant


@api.get("/tenants/")
@login_required
@jsonify_response
def get_all_tenants():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    search_term = request.args.get("q", "", type=str)

    tenants_query = VNTenant.get_tenants_list().filter(
        db.or_(
            VNTenant.vn_fullname.ilike(f"%{search_term}%"),
            VNTenant.vn_addr_email.ilike(f"%{search_term}%"),
            VNTenant.vn_phonenumber_one.ilike(f"%{search_term}%"),
            db.or_(
                hasattr(VNTenant, "vn_cni_number"),
                VNTenant.vn_cni_number.ilike(f"%{search_term}%"),
            ),
            db.or_(
                hasattr(VNTenant, "vn_phonenumber_two"),
                VNTenant.vn_phonenumber_two.ilike(f"%{search_term}%"),
            ),
            db.or_(
                hasattr(VNTenant, "vn_location"),
                VNTenant.vn_location.ilike(f"%{search_term}%"),
            ),
        )
    )

    pagination = tenants_query.paginate(page=page, per_page=per_page, error_out=False)

    prev = (
        url_for("api.get_all_tenants", page=page - 1, _external=True)
        if pagination.has_prev
        else None
    )
    next = (
        url_for("api.get_all_tenants", page=page + 1, _external=True)
        if pagination.has_next
        else None
    )

    return {
        "tenants": [houses.tenant_schema.dump(t) for t in pagination.items],
        "user": users.user_schema.dump(current_user),
        "prev": prev,
        "next": next,
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
    }


@api.get("/tenants/<string:uuid>/")
@login_required
@jsonify_response
@cache.cached(timeout=500)
def get_tenant(uuid: str) -> dict:
    tenant = abort_if_tenant_doesnt_exist(uuid)
    return {"tenant": houses.tenant_schema.dump(tenant)}


@api.delete("/tenants/<string:uuid>/")
@login_required
@jsonify_response
def delete_tenant(uuid: str) -> dict:
    tenant = abort_if_tenant_doesnt_exist(uuid)
    tenant.house.house_disable()
    tenant.remove()
    return {
        "success": True,
        "message": f"Locataire #{tenant.vn_tenant_id} a été supprimé avec succès !",
    }


@api.patch("/tenants/<string:uuid>/")
@login_required
@jsonify_response
def update_tenant(uuid: str) -> dict:
    tenant = abort_if_tenant_doesnt_exist(uuid)

    update_tenant_data = request.json.get("update_tenant_data")

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
        if field in update_tenant_data:
            setattr(tenant, field, update_tenant_data[field])
    tenant.save()

    return {
        "success": True,
        "message": f"Locataire #{tenant.vn_tenant_id} mise à jour avec succès !",
    }
