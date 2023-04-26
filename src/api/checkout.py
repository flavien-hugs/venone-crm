from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from src.payment import VNPayment
from src.payment import VNTransferRequest
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


@api.get("/transfers-request/")
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
        "transfers": [transfer.to_json() for transfer in transfers],
        "prev": prev,
        "next": next,
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "user": current_user.to_json(),
    }


@api.post("/transfers-request/create/")
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

    if (trans_amount := transfer_data.get("trans_amount")) is None or (
        withdrawal_number := transfer_data.get("withdrawal_number")
    ) is None:
        return {
            "success": False,
            "message": "Montant de transfert ou numéro de retrait\
                manquant dans les données de transfert",
        }

    if trans_amount < 20000:
        return {
            "success": False,
            "message": "Le montant de retrait doit être supérieur ou égal à 20 000",
        }

    transfer = VNTransferRequest()

    transfer.vn_user_id = user
    transfer.vn_trans_amount = trans_amount
    transfer.vn_withdrawal_number = withdrawal_number

    transfer.save()

    return {"success": True, "message": "Demande de transfert soumis avec succès !"}
