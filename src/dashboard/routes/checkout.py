from flask import Blueprint
from flask import render_template
from flask_login import current_user
from flask_login import login_required
from src.exts import cache


checkout_bp = Blueprint("checkout_bp", __name__, url_prefix="/dashboard/")


@checkout_bp.get("/payments/")
@login_required
# @cache.cached(timeout=500)
def checkout():
    page_title = "Liste des paiements de loyers"
    return render_template(
        "checkout/checkout.html", page_title=page_title, current_user=current_user
    )


@checkout_bp.get("/requests/")
@login_required
def transfer_request():
    page_title = "Retraits"
    return render_template(
        "checkout/transfer.html", page_title=page_title, current_user=current_user
    )
