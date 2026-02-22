from flask import request, url_for
from flask_login import current_user, login_required

from src.exts import db
from src.payment import VNPayment, VNTransferRequest
from src.schemas import houses, users
from src.utils import jsonify_response

from . import api
from .user import abort_if_user_doesnt_exist


@api.get("/payments/")
@login_required
@jsonify_response
def get_all_payments():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = VNPayment.paids()
    payments_items = db.paginate(
        query, page=page, per_page=per_page, max_per_page=20, error_out=True, count=True
    )
    payments_ids = payments_items.items

    prev = (
        url_for("api.get_all_payments", page=page - 1, _external=True)
        if payments_items.has_prev
        else None
    )
    next = (
        url_for("api.get_all_payments", page=page + 1, _external=True)
        if payments_items.has_next
        else None
    )

    return {
        "payments": [houses.payment_schema.dump(payment) for payment in payments_ids],
        "user": users.user_schema.dump(current_user),
        "prev": prev,
        "next": next,
        "page": page,
        "per_page": per_page,
        "total": payments_items.total,
    }


@api.get("/transfers/")
@login_required
@jsonify_response
def get_transfers():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = VNTransferRequest.get_transfers_request().paginate(
        page=page, per_page=per_page, error_out=False
    )

    transfers = pagination.items
    prev = (
        url_for("api.get_transfers", page=page - 1, _external=True)
        if pagination.has_prev
        else None
    )
    next = (
        url_for("api.get_transfers", page=page + 1, _external=True)
        if pagination.has_next
        else None
    )

    return {
        "transfers": [houses.transfer_schema.dump(t) for t in transfers],
        "user": users.user_schema.dump(current_user),
        "prev": prev,
        "next": next,
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
    }


@api.post("/transfers/")
@login_required
@jsonify_response
def create_transfer_request():
    abort_if_user_doesnt_exist(current_user.uuid)

    transfer_data = request.json.get("transfer_data")
    if transfer_data is None:
        return {
            "success": False,
            "message": "Données de transfert manquantes dans la requête",
        }

    vn_trans_amount = transfer_data.get("vn_trans_amount")
    vn_withdrawal_number = transfer_data.get("vn_withdrawal_number")
    if vn_trans_amount is None or vn_withdrawal_number is None:
        return {
            "success": False,
            "message": "Montant de transfert ou numéro de retrait manquant dans les données de transfert",
        }

    if vn_trans_amount < 20_000:
        return {
            "success": False,
            "message": "Le montant de retrait doit être supérieur ou égal à 20 001",
        }

    if (
        current_user.get_total_payments_received() is not None
        and vn_trans_amount >= current_user.get_total_payments_received()
    ):
        return {
            "success": False,
            "message": "Vous n'aviez pas assez de fonds disponibles pour le transfert.",
        }

    _ = current_user.request_transfer(
        vn_trans_amount, vn_withdrawal_number
    )
    current_user.deduct_payments_received(int(vn_trans_amount))

    return {"success": True, "message": "Demande de transfert soumis avec succès !"}
