from flask import jsonify
from flask import request
from flask import url_for
from flask_login import login_required
from src.auth.models import VNUser

from . import api


@api.get("/users/")
@login_required
def get_all_users():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = VNUser.get_users_list().paginate(
        page=page, per_page=per_page, error_out=False
    )

    users = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for("api.get_all_users", page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for("api.get_all_users", page=page + 1, _external=True)

    return jsonify(
        {
            "houseowners": [user.to_json() for user in users],
            "prev": prev,
            "next": next,
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
        }
    )


@api.get("/user/")
@login_required
def get_user():
    user = VNUser.get_user_logged()
    return jsonify({"user": user.to_json()})


@api.route("/user/<string:user_uuid>/owners/")
@login_required
def get_user_owners(user_uuid):

    user = VNUser.get_user(user_uuid)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = user.houseowners.paginate(
        page=page, per_page=per_page, error_out=False
    )
    owners = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for("api.get_user_owners", page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for("api.get_user_owners", page=page + 1, _external=True)

    return jsonify(
        {
            "owners": [owner.to_json() for owner in owners],
            "prev": prev,
            "next": next,
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
        }
    )


@api.route("/user/<string:user_uuid>/tenants/")
@login_required
def get_user_tenants(user_uuid):

    user = VNUser.get_user(user_uuid)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = user.tenants.paginate(page=page, per_page=per_page, error_out=False)
    tenants = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for("api.get_user_tenants", page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for("api.get_user_tenants", page=page + 1, _external=True)

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


@api.route("/user/<string:user_uuid>/houses/")
@login_required
def get_user_houses(user_uuid):

    user = VNUser.get_user(user_uuid)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = user.houses.paginate(page=page, per_page=per_page, error_out=False)
    houses = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for("api.get_user_houses", page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for("api.get_user_houses", page=page + 1, _external=True)

    return jsonify(
        {
            "houses": [house.to_json() for house in houses],
            "prev": prev,
            "next": next,
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
        }
    )


@api.route("/user/<string:user_uuid>/payments/")
@login_required
def get_user_payments(user_uuid):

    user = VNUser.get_user(user_uuid)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = user.payments.paginate(page=page, per_page=per_page, error_out=False)
    payments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for("api.get_user_payments", page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for("api.get_user_payments", page=page + 1, _external=True)

    return jsonify(
        {
            "payments": [pay.to_json() for pay in payments],
            "prev": prev,
            "next": next,
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
        }
    )
