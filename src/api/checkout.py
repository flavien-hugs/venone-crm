from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from src.payment import VNPayment
from src.utils import jsonify_response

from . import api


@api.get("/payments/")
@login_required
@jsonify_response
def get_all_payments():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = VNPayment.get_payments().paginate(
        page=page, per_page=per_page, error_out=False
    )

    payments = pagination.items
    prev = (
        url_for("api.get_all_payments", page=page - 1, _external=True)
        if pagination.has_prev
        else None
    )
    next = (
        url_for("api.get_all_payments", page=page + 1, _external=True)
        if pagination.has_next
        else None
    )

    return {
        "payments": [payment.to_json() for payment in payments],
        "prev": prev,
        "next": next,
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "user": current_user.to_json(),
    }
