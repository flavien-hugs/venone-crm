from flask import Blueprint
from flask import render_template
from flask_login import current_user
from flask_login import login_required


dashboard_view = Blueprint("dashboard_view", __name__, url_prefix="/customer/dashboard/")


@dashboard_view.route("/api/", methods=["GET"])
@login_required
def api():
    from flask import jsonify
    data = {
        "id": current_user.id,
        "addr_email": current_user.vn_user_addr_email
    }
    return jsonify({"data": data}), 200


@dashboard_view.route("/index/", methods=["GET"])
@login_required
def dashboard():
    page_title = "Tableau de board"
    return render_template(
        "auth/admin/dashboard.html",
        page_title=page_title,
        current_user=current_user
    )
