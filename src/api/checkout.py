from flask import render_template, request, url_for
from flask_login import current_user, login_required

from src.core import get_user_service
from src.infrastructure.config.plugins import db
from .__main__ import api_bp
from .users import abort_if_user_doesnt_exist


@api_bp.get("/payments/")
@login_required
def get_all_payments():
    page = request.args.get("page", 1, type=int)
    per_page = 20

    user_service = get_user_service()
    query = user_service.get_payments_list(current_user.id).filter_by(
        vn_pay_status=True
    )

    search_term = request.args.get("q", "", type=str)
    if search_term:
        from src.infrastructure.persistence.models import Tenant, Payment

        query = query.join(Tenant, isouter=True).filter(
            db.or_(
                Payment.vn_transaction_id.ilike(f"%{search_term}%"),
                Payment.vn_payment_method.ilike(f"%{search_term}%"),
                Payment.vn_operator_id.ilike(f"%{search_term}%"),
                Tenant.vn_fullname.ilike(f"%{search_term}%"),
            )
        )

    pagination = db.paginate(
        query, page=page, per_page=per_page, max_per_page=20, error_out=False
    )

    return render_template(
        "checkout/partials/payments_table.html",
        payments=pagination.items,
        pagination=pagination,
        page=page,
        current_user=current_user,
    )


@api_bp.get("/transfers/")
@login_required
def get_transfers():
    page = request.args.get("page", 1, type=int)
    per_page = 10

    user_service = get_user_service()
    pagination = user_service.get_transfers_request(current_user.id).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        "checkout/partials/transfers_table.html",
        transfers=pagination.items,
        pagination=pagination,
        page=page,
        current_user=current_user,
    )


@api_bp.post("/transfers/")
@login_required
def create_transfer_request():
    from flask import flash, redirect

    abort_if_user_doesnt_exist(current_user.uuid)

    vn_trans_amount = request.form.get("vn_trans_amount", type=float)
    vn_withdrawal_number = request.form.get("vn_withdrawal_number", "").strip()

    error = None
    if not vn_trans_amount or not vn_withdrawal_number:
        error = "Veuillez remplir tous les champs."
    elif vn_trans_amount < 20_000:
        error = "Le montant minimum de retrait est de 20 000."
    else:
        user_service = get_user_service()
        total_received = user_service.get_total_payments_received(current_user.id)
        if vn_trans_amount > total_received:
            error = "Solde insuffisant pour ce montant."

    if error:
        flash(error, "danger")
    else:
        user_service = get_user_service()
        user_service.request_transfer(
            current_user.id, vn_trans_amount, vn_withdrawal_number
        )
        user_service.deduct_balance(current_user.id, int(vn_trans_amount))
        flash("Demande de retrait soumise avec succès !", "success")

    return redirect(url_for("checkout_bp.transfer_request"))
