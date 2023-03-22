import os
import random
import string
from datetime import datetime

import pyshorteners
import requests
from cinetpay_sdk.s_d_k import Cinetpay
from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import request
from flask import url_for
from src.payment import VNPayment
from src.tenant import VNHouse

main_bp = Blueprint("main_bp", __name__, url_prefix="/")


@main_bp.get("/payment/<string:house_uuid>/")
def process_payment(house_uuid):

    app = current_app._get_current_object()
    SITEID = app.config["CINETPAY_SITE_ID"]
    APIKEY = app.config["CINETPAY_API_KEY"]

    client = Cinetpay(APIKEY, SITEID)

    house = VNHouse.query.filter_by(uuid=house_uuid).first()

    if house is not None:
        transaction_id = "".join(random.choices(string.digits, k=8))

        house_id = house.vn_house_id
        amount = house.vn_house_rent
        tenant = house.get_current_tenant()
        device = house.user_houses.vn_device
        phonenumber_one = house.get_tenant_phone_number()

        notify_url = redirect(
            url_for("main_bp.payment_success", house_uuid=house.uuid, _external=True)
        )
        print(notify_url)

        data = {
            "amount": amount,
            "currency": device,
            "transaction_id": transaction_id,
            "description": f"Paiement du loyer {house_id}",
            "return_url": "https://g.venone.app/payment/cancel",
            "notify_url": notify_url,
            "customer_name": tenant,
            "customer_surname": tenant,
        }
        response = client.PaymentInitialization(data)

        payment_url = response["data"]["payment_url"]
        print(payment_url)
        return redirect(payment_url)
    else:
        pass


def send_sms_reminder(house, tenant):

    current_date = datetime.utcnow().date()
    app = current_app._get_current_object()

    SMS_API_KEY = app.config["SMS_API_KEY"]
    SMS_BASE_URL = app.config["SMS_BASE_URL"]
    SMS_SENDER_ID = app.config["SMS_SENDER_ID"]
    SMS_API_TOKEN = app.config["SMS_API_TOKEN"]

    fullname = house.get_current_tenant()
    phone_number = house.get_tenant_phone_number()
    house_lease_end = house.vn_house_lease_end_date

    payment_response = redirect(
        url_for("main_bp.process_payment", house_uuid=house.uuid, _external=True)
    )
    payment_url = payment_response.headers["Location"]

    s = pyshorteners.Shortener()
    short_url = (
        s.dagd.short(payment_url)
        if not payment_url.startswith(("http://", "https://"))
        else payment_url
    )
    print(short_url)

    message = f"Bonjour {fullname}, votre facture de loyer\
    du mois de {house_lease_end} est prête.\
    Veuillez cliquer sur ce lien: {short_url} pour procéder au paiement. Merci, Venone."

    reqUrl = f"{SMS_BASE_URL}?sendsms&apikey={SMS_API_KEY}\
    &apitoken={SMS_API_TOKEN}&type=sms&from={SMS_SENDER_ID}&to={phone_number}&text={message}"

    if current_date <= house_lease_end and not VNHouse.is_rent_paid(house):
        requests.request("POST", reqUrl)


@main_bp.route("/payment/success/<house_uuid>/")
def payment_success(house_uuid):

    house = VNHouse.query.filter_by(uuid=house_uuid).first()

    current_date = datetime.utcnow().date()
    transaction_id = request.args.get("transaction_id")

    CINETPAY_SITEID = os.getenv("CINETPAY_SITEID")
    CINETPAY_APIKEY = os.getenv("CINETPAY_APIKEY")

    client = Cinetpay(CINETPAY_APIKEY, CINETPAY_SITEID)
    token = client.TransactionVerfication_token(transaction_id)
    print(token)

    if token:
        payment = VNPayment(
            vn_transaction_id=transaction_id,
            vn_pay_amount=house.vn_house_rent,
            vn_payee_id=house.vn_user_id,
            vn_owner_id=house.vn_owner_id,
            vn_tenant_id=house.tenant_payment.id,
            vn_house_id=house.id,
            vn_pay_status=True,
            vn_pay_date=current_date,
        )
        payment.save()
        return "OK"
    else:
        return "ERROR"
