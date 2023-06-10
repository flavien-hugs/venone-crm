from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from src.payment import VNPayment
from src.payment import VNTransferRequest
from src.schemas import houses
from src.schemas import users
from src.utils import jsonify_response

from . import api


@api.get("/payments/")
@login_required
@jsonify_response
def get_all_payments():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = VNPayment.paids().paginate(
        page=page, per_page=per_page, error_out=False
    )
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
        "payments": [
            houses.payment_schema.dump(payment) for payment in pagination.items
        ],
        "user": users.user_schema.dump(current_user),
        "prev": prev,
        "next": next,
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
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
        "transfers": [houses.transfers_schema.dump(t) for t in transfers],
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

    user = current_user.id

    if not user:
        return {"success": False, "message": "Oups ! L'élément n'a pas été trouvé"}

    if (transfer_data := request.json.get("transfer_data")) is None:
        return {
            "success": False,
            "message": "Données de transfert manquantes dans la requête",
        }

    if (vn_trans_amount := transfer_data.get("vn_trans_amount")) is None or (
        vn_withdrawal_number := transfer_data.get("vn_withdrawal_number")
    ) is None:
        return {
            "success": False,
            "message": "Montant de transfert ou numéro de retrait\
                manquant dans les données de transfert",
        }

    if vn_trans_amount < 20000:
        return {
            "success": False,
            "message": "Le montant de retrait doit être supérieur ou égal à 20 001",
        }

    if current_user.vn_balance < vn_trans_amount:
        return {
            "success": False,
            "message": "Vous n'aviez pas assez de fonds disponibles pour le transfert.",
        }

    transfer_amount = current_user.request_transfer(
        vn_trans_amount, vn_withdrawal_number
    )
    current_user.deduct_payments_received(vn_trans_amount)
    transfer_amount.save()

    return {"success": True, "message": "Demande de transfert soumis avec succès !"}
