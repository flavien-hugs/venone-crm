from flask import jsonify
from flask_login import login_required
from src.auth.models import VNUser

from . import api


@api.get("/owners/data/")
@login_required
def get_owners_data():
    data = VNUser.get_ownerbymonth()
    return jsonify([{"month": d[0], "count": d[1]} for d in data])


@api.get("/tenants/data/")
@login_required
def get_tenants_data():
    data = VNUser.get_tenantbymonth()
    return jsonify([{"month": d[0], "count": d[1]} for d in data])


@api.get("/trendprices/data/")
@login_required
def get_trendprices_data():
    data = VNUser.get_trendprices()
    return jsonify([{"month": d[0], "price": d[1]} for d in data])


@api.get("/available_properties/data/")
@login_required
def get_available_properties_data():
    data = VNUser.count_available_properties()
    return jsonify([{"isOpen": d[0], "notOpen": d[1]} for d in data])
