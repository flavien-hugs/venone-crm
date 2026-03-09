from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import current_user, login_required

from src.core import get_payment_service, get_user_service
from src.infrastructure.config.plugins import db
from src.infrastructure.persistence.models import Payment, TransferRequest

checkout_bp = Blueprint("checkout_bp", __name__, url_prefix="/dashboard/")


@checkout_bp.get("/payments/")
@login_required
def checkout():
    page_title = "Liste des paiements de loyers"
    return render_template(
        "checkout/checkout.html", page_title=page_title, current_user=current_user
    )

@checkout_bp.get("/requests/")
@login_required
def transfer_request():
    page_title = "Retraits"
    user_service = get_user_service()
    total_received = user_service.get_total_payments_received(current_user.id)
    total_house_amount = user_service.calculate_total_houses_amount(current_user.id)
    total_percent = user_service.calculate_amount_apply_percent(current_user.id)
    return render_template(
        "checkout/transfer.html",
        page_title=page_title,
        current_user=current_user,
        total_received=total_received,
        total_house_amount=total_house_amount,
        total_percent=total_percent,
    )


@checkout_bp.get("/payments/export/")
@login_required
def export_payments_csv():
    """Generates a CSV of paid payments for the current user."""
    from src.dashboard.services import export_data
    from datetime import datetime
    from flask import Response

    payment_service = get_payment_service()
    payments = payment_service.repository.find_paids(current_user.id).all()

    headers = [
        "ID Transaction",
        "ID Opérateur",
        "Locataire",
        "Montant",
        "Méthode",
        "Date",
    ]

    csv_data = export_data.generate_payments_csv(payments, headers)
    current_date = datetime.now().strftime("%d-%m-%Y")

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-disposition": f"attachment; filename=paiements_{current_date}.csv"
        }
    )


@checkout_bp.get("/requests/export/")
@login_required
def export_transfers_csv():
    """Generates a CSV of transfer requests for the current user."""
    import csv
    import io
    from datetime import datetime
    from flask import Response

    transfers = TransferRequest.query.filter_by(vn_user_id=current_user.id).order_by(db.desc(TransferRequest.vn_created_at)).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID Retrait", "Numéro", "Montant", "Date", "Statut"])

    for t in transfers:
        writer.writerow([
            t.vn_transfer_id,
            t.vn_withdrawal_number,
            t.vn_trans_amount,
            t.vn_created_at.strftime('%Y-%m-%d %H:%M') if t.vn_created_at else '',
            "Validé" if t.vn_trans_status else "En attente"
        ])

    csv_data = output.getvalue()
    current_date = datetime.now().strftime("%d-%m-%Y")

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-disposition": f"attachment; filename=retraits_{current_date}.csv"
        }
    )
