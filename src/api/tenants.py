from http import HTTPStatus

from flask import abort, request, url_for, render_template
from flask_login import current_user, login_required

from src.api.schemas import houses, users
from src.core import get_user_service
from src.infrastructure.config.plugins import cache, db
from src.infrastructure.persistence.models import Tenant, House, HouseOwner
from .__main__ import api_bp
from .shared.helpers import jsonify_response


def abort_if_tenant_doesnt_exist(uuid: str):
    tenant = Tenant.query.filter_by(vn_tenant_id=uuid).first()
    if not tenant:
        abort(HTTPStatus.NOT_FOUND, f"Could not find tenant with ID {uuid}")
        
    if not current_user.is_administrator() and tenant.vn_user_id != current_user.id:
        abort(HTTPStatus.FORBIDDEN, "Access denied")
        
    return tenant


@api_bp.get("/tenants/")
@login_required
def get_all_tenants():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    search_term = request.args.get("q", "", type=str)

    user_service = get_user_service()
    tenants_query = user_service.get_tenants_list(current_user.id)
    
    if search_term:
        tenants_query = tenants_query.join(House, isouter=True).join(HouseOwner, isouter=True).filter(
            db.or_(
                Tenant.vn_fullname.ilike(f"%{search_term}%"),
                Tenant.vn_addr_email.ilike(f"%{search_term}%"),
                Tenant.vn_phonenumber_one.ilike(f"%{search_term}%"),
                Tenant.vn_cni_number.ilike(f"%{search_term}%"),
                Tenant.vn_phonenumber_two.ilike(f"%{search_term}%"),
                Tenant.vn_location.ilike(f"%{search_term}%"),
                House.vn_house_address.ilike(f"%{search_term}%"),
                HouseOwner.vn_fullname.ilike(f"%{search_term}%"),
            )
        )

    pagination = tenants_query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template("tenant/partials/_tenant_list.html", tenants=pagination, current_user=current_user)


@api_bp.get("/tenants/<string:uuid>/")
@login_required
@jsonify_response
@cache.cached(timeout=500)
def get_tenant(uuid: str) -> dict:
    tenant = abort_if_tenant_doesnt_exist(uuid)
    return {"tenant": houses.tenant_schema.dump(tenant)}


@api_bp.delete("/tenants/<string:uuid>/")
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


@api_bp.patch("/tenants/<string:uuid>/")
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
