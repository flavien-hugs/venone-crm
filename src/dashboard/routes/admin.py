from flask import Blueprint, render_template
from flask_login import current_user, login_required

from src.core import get_user_service
from src.api.middlewares import admin_required

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin/dashboard/")


@admin_bp.get("/-/")
@login_required
@admin_required
def dashboard():
    page_title = "Tableau de board"
    user_service = get_user_service()

    stats = user_service.get_dashboard_stats(current_user.id)

    owner_data = user_service.get_owner_per_month(current_user.id)
    tenant_data = user_service.get_tenant_per_month(current_user.id)
    open_houses_data = user_service.houses_opened_count(current_user.id)
    trend_price_data = user_service.get_trendprices(current_user.id)

    return render_template(
        "dashboard/dashboard.html",
        page_title=page_title,
        current_user=current_user,
        stats=stats,
        owner_data=owner_data,
        tenant_data=tenant_data,
        open_houses_data=open_houses_data,
        trend_price_data=trend_price_data,
    )
