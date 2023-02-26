from datetime import datetime
from datetime import timedelta

from flask import jsonify
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from src import db
from src.tenant import VNHouse
from src.tenant import VNHouseOwner
from src.tenant import VNTenant

from . import api


@api.get("/tenants/")
@login_required
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

    prev = None
    if pagination.has_prev:
        prev = url_for(
            "api.get_all_tenants", page=page - 1, q=search_term, _external=True
        )
    next = None
    if pagination.has_next:
        next = url_for(
            "api.get_all_tenants", page=page - 1, q=search_term, _external=True
        )

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


@api.post("/tenant/register/")
@login_required
def register_tenant():

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
            lease_start_date + timedelta(days=lease_duration_days) - notice_period
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


@api.delete("/tenant/<string:tenant_uuid>/delete/")
@login_required
def delete_tenant(tenant_uuid):
    tenant = VNTenant.get_tenant(tenant_uuid)
    tenant.house_tenant.disable()
    tenant.house_tenant.house_disable()

    print("delete tenant : ", tenant.house_tenant.house_disable())

    if tenant is not None:
        tenant.disable()
        return jsonify(
            {
                "success": True,
                "message": f"Locataire #{tenant.vn_tenant_id} a été supprimé avec succès !",
            }
        )
    return jsonify(
        {
            "success": False,
            "message": "Oups ! L'élément n'a pas été trouvé.",
        }
    )


@api.put("/tenant/<string:tenant_uuid>/update/")
@login_required
def update_tenant(tenant_uuid):
    tenant = VNTenant.get_tenant(tenant_uuid)

    if not tenant:
        return jsonify({"message": "tenant not found"}), 404

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

    return (
        jsonify(
            {
                "success": True,
                "message": f"Locataire #{tenant.vn_tenant_id} mise à jour avec succès !",
                "tenant": tenant.to_json(),
            }
        ),
        200,
    )


@api.get("/tenant/<string:tenant_uuid>/")
@login_required
def get_tenant(tenant_uuid):
    tenant = VNTenant.get_tenant(tenant_uuid)
    return jsonify({"tenant": tenant.to_json()})
