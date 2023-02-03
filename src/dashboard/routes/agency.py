from flask import Blueprint
from flask import render_template
from flask_login import current_user
from flask_login import login_required

from src.auth.models import VNUser


agency_bp = Blueprint("agency_bp", __name__, url_prefix="/customer/dashboard/")


@agency_bp.route("/api/", methods=["GET"])
@login_required
def api():
    from flask import jsonify
    data = {
        "id": current_user.id,
        "addr_email": current_user.vn_user_addr_email
    }
    return jsonify({"data": data}), 200


@agency_bp.route("/index/", methods=["GET"])
@login_required
def dashboard():
    page_title = "Tableau de board"
    return render_template(
        "auth/admin/dashboard.html",
        page_title=page_title,
        username=current_user.get_name()
    )


@agency_bp.route("/settings/", methods=["GET"])
@login_required
def setting():
    page_title = "Paramètres"
    return render_template(
        "auth/admin/pages/company/settings.html",
        page_title=page_title,
        username=current_user.get_name()
    )
