from flask import jsonify
from flask import make_response
from flask_login import login_required
from src.auth.models import VNUser

from . import api


@api.get("/owners/data/")
@login_required
def get_owners_data():
    data = VNUser.get_ownerbymonth()
    return make_response(
        jsonify([{"year": d[0], "month": d[1], "count": d[2]} for d in data])
    )


@api.get("/tenants/data/")
@login_required
def get_tenants_data():
    data = VNUser.get_tenantbymonth()
    return make_response(
        jsonify([{"year": d[0], "month": d[1], "count": d[2]} for d in data])
    )


@api.get("/trendprices/data/")
@login_required
def get_trendprices_data():
    data = VNUser.get_trendprices()
    return make_response(
        jsonify([{"year": d[0], "month": d[1], "price": d[2]} for d in data])
    )


@api.get("/available_properties/data/")
@login_required
def get_available_properties_data():
    data = VNUser.count_available_properties()
    return make_response(jsonify([{"isOpen": d[0], "notOpen": d[1]} for d in data]))
