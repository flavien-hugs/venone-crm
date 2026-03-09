from flask_login import current_user, login_required

from src.core import get_user_service
from .__main__ import api_bp
from .shared.helpers import jsonify_response


@api_bp.get("/owners/data/")
@login_required
@jsonify_response
def get_owners_data():
    user_service = get_user_service()
    data = user_service.get_owner_per_month(current_user.id)
    return [{"year": d[0], "month": d[1], "count": d[2]} for d in data]


@api_bp.get("/tenants/data/")
@login_required
@jsonify_response
def get_tenants_data():
    user_service = get_user_service()
    data = user_service.get_tenant_per_month(current_user.id)
    return [{"year": d[0], "month": d[1], "count": d[2]} for d in data]


@api_bp.get("/trendprices/data/")
@login_required
@jsonify_response
def get_trendprices_data():
    user_service = get_user_service()
    data = user_service.get_trendprices(current_user.id)
    return [{"year": d[0], "month": d[1], "price": d[2]} for d in data]


@api_bp.get("/availables-houses/data/")
@login_required
@jsonify_response
def get_available_properties_data():
    user_service = get_user_service()
    return user_service.houses_opened_count(current_user.id)
