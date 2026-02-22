from flask import Blueprint, render_template
from flask_login import current_user, login_required

from src.mixins.decorators import admin_required

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin/dashboard/")


@admin_bp.get("/")
@login_required
@admin_required
def dashboard():
    page_title = "Tableau de board"
    return render_template(
        "dashboard/dashboard.html", page_title=page_title, current_user=current_user
    )
