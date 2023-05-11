from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from src.exts import db
from src.tenant import VNTenant
from src.utils import jsonify_response

from . import api


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
    tenants = pagination.items

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
        "tenants": [tenant.to_json() for tenant in tenants],
        "prev": prev,
        "next": next,
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "user": current_user.to_json(),
    }


@api.delete("/tenants/<string:tenant_uuid>/delete/")
@login_required
@jsonify_response
def delete_tenant(tenant_uuid):
    tenant = VNTenant.get_tenant(tenant_uuid)

    if tenant is not None:
        tenant.house_tenant.house_disable()
        tenant.remove()
        return {
            "success": True,
            "message": f"Locataire #{tenant.vn_tenant_id} a été supprimé avec succès !",
        }

    return {
        "success": False,
        "message": "Oups ! L'élément n'a pas été trouvé.",
    }


@api.put("/tenants/<string:tenant_uuid>/update/")
@login_required
@jsonify_response
def update_tenant(tenant_uuid):
    tenant = VNTenant.get_tenant(tenant_uuid)

    if not tenant:
        return {"message": "tenant not found"}

    data = request.json

    fullname = data.get("fullname")
    addr_email = data.get("addr_email")
    card_number = data.get("card_number")
    profession = data.get("profession")
    parent_name = data.get("parent_name")
    phonenumber_one = data.get("phonenumber_one")
    phonenumber_two = data.get("phonenumber_two")

    tenant.vn_fullname = fullname
    tenant.vn_addr_email = addr_email
    tenant.vn_cni_number = card_number
    tenant.vn_profession = profession
    tenant.vn_parent_name = parent_name
    tenant.vn_phonenumber_one = phonenumber_one
    tenant.vn_phonenumber_two = phonenumber_two

    tenant.save()

    return {
        "success": True,
        "message": f"Locataire #{tenant.vn_tenant_id} mise à jour avec succès !",
    }


@api.get("/tenants/<string:tenant_uuid>/")
@login_required
@jsonify_response
def get_tenant(tenant_uuid):
    tenant = VNTenant.get_tenant(tenant_uuid)
    if not tenant:
        return {
            "message": "Oups ! L'élément n'a pas été trouvé !",
        }

    return {"tenant": tenant.to_json()}
