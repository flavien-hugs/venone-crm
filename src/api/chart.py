from flask_login import current_user
from flask_login import login_required
from src.utils import jsonify_response

from . import api


@api.get("/owners/data/")
@login_required
@jsonify_response
def get_owners_data():
    data = current_user.get_owner_per_month()
    return [{"year": d[0], "month": d[1], "count": d[2]} for d in data]


@api.get("/tenants/data/")
@login_required
@jsonify_response
def get_tenants_data():
    data = current_user.get_tenant_per_month()
    return [{"year": d[0], "month": d[1], "count": d[2]} for d in data]


@api.get("/trendprices/data/")
@login_required
@jsonify_response
def get_trendprices_data():
    data = current_user.get_trendprices()
    return [{"year": d[0], "month": d[1], "price": d[2]} for d in data]


@api.get("/availables-houses/data/")
@login_required
@jsonify_response
def get_available_properties_data():
    data = current_user.houses_opened_count()
    return [{"isOpen": d[0], "notOpen": d[1]} for d in data]
