from flask import render_template
from flask_login import current_user
from flask_login import login_required

from .. import owner_view


@owner_view.route("/", methods=["GET"])
@login_required
def owner_dashboard():
    page_title = "Tableau de board"

    return render_template(
        "admin/dashboard.html", page_title=page_title, current_user=current_user
    )
