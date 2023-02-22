from flask import jsonify
from flask import request
from flask import url_for
from flask_login import login_required
from src.tenant import VNTenant

from . import api


@api.get("/tenants/")
@login_required
def get_all_tenants():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = VNTenant.get_tenants_list().paginate(
        page=page, per_page=per_page, error_out=False
    )

    tenants = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for("api.get_all_tenants", page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for("api.get_all_tenants", page=page + 1, _external=True)

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


@api.delete("/tenant/<string:tenant_uuid>/delete/")
@login_required
def delete_tenant(tenant_uuid):
    tenant = VNTenant.get_tenant(tenant_uuid)
    if tenant is not None:
        tenant.delete()
        return jsonify(
            {
                "success": True,
                "message": f"Le locataire {tenant} a été supprimé avec succès.",
            }
        )
    return jsonify(
        {
            "success": False,
            "message": f"L'élément avec l'id {tenant_uuid} n'a pas été trouvé.",
        }
    )


@api.put("/tenant/<string:tenant_uuid>/update/")
@login_required
def update_tenant(tenant_uuid):
    tenant = VNTenant.get_tenant(tenant_uuid)

    if not tenant:
        return jsonify({"message": "tenant not found"}), 404

    data = request.get_json()
    fullname = data.get("fullname")
    addr_email = data.get("addr_email")
    card_number = data.get("card_number")
    location = data.get("location")
    profession = data.get("profession")
    parent_name = data.get("parent_name")
    phonenumber_one = data.get("phonenumber_one")
    phonenumber_two = data.get("phonenumber_two")

    tenant.vn_fullname = fullname
    tenant.vn_addr_email = addr_email
    tenant.vn_cni_number = card_number
    tenant.vn_location = location
    tenant.vn_profession = profession
    tenant.vn_parent_name = parent_name
    tenant.vn_phonenumber_one = phonenumber_one
    tenant.vn_phonenumber_two = phonenumber_two

    tenant.save()

    return (
        jsonify(
            {
                "success": True,
                "message": f"tenant {tenant.vn_tenant_id} updated successfully",
                "tenant": tenant.to_json(),
            }
        ),
        200,
    )


@api.get("/tenant/<string:uuid>/")
@login_required
def get_tenant(uuid):
    tenant = VNTenant.get_tenant(uuid)
    return jsonify(tenant.to_json())
