from flask import Blueprint
from flask import render_template
from flask_login import current_user
from flask_login import login_required


admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin/dashboard/")


@admin_bp.route("/index/", methods=["GET"])
@login_required
def dashboard():
    page_title = "Tableau de board"
    return render_template(
        "auth/admin/dashboard.html",
        page_title=page_title,
        current_user=current_user
    )
