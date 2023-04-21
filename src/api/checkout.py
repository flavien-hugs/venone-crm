from flask import jsonify
from flask import make_response
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from src.payment import VNPayment

from . import api


@api.get("/payments/")
@login_required
def get_all_payments():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = VNPayment.get_payment_list().paginate(
        page=page, per_page=per_page, error_out=False
    )

    payments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for("api.get_all_payments", page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for("api.get_all_payments", page=page + 1, _external=True)

    return make_response(
        jsonify(
            {
                "payments": [payment.to_json() for payment in payments],
                "prev": prev,
                "next": next,
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "user": current_user.to_json(),
            }
        )
    )
