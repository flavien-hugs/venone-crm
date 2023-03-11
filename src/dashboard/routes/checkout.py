from flask import Blueprint
from flask import render_template
from flask_login import current_user
from flask_login import login_required


checkout_bp = Blueprint("checkout_bp", __name__, url_prefix="/dashboard/")


@checkout_bp.get("/checkout/")
@login_required
def checkout():
    page_title = "Loyers"
    return render_template(
        "checkout/checkout.html",
        page_title=page_title,
        current_user=current_user
    )
