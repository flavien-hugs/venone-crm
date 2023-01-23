from flask import Blueprint
from flask import render_template
from flask_login import current_user
from flask_login import login_required


dashboard_view = Blueprint("dashboard_view", __name__)


@dashboard_view.route("/dashboard/", methods=["GET"])
@login_required
def dashboard():
    page_title = "Tableau de board"
    return render_template(
        "auth/admin/dashboard.html",
        page_title=page_title,
        current_user=current_user,
    )
