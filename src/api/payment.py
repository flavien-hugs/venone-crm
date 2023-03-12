from flask import jsonify
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required

from src import db
from src.payment import VNPayment

from . import api


@api.get("/payments/")
@login_required
def get_payments():
    payments = VNPayment.tenants_paids()
    return jsonify(payments)
