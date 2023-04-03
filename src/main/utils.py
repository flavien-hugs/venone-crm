import os
import random
import string
import logging as lg
from datetime import datetime

import pyshorteners
import requests
from flask import current_app
from flask import redirect
from flask import request
from flask import url_for
from src.payment import VNPayment
from src.tenant import VNHouse

from cinetpay_sdk.s_d_k import Cinetpay

def process_payment(house):

    app = current_app._get_current_object()
    SITEID = app.config["CINETPAY_SITE_ID"]
    APIKEY = app.config["CINETPAY_API_KEY"]

    client = Cinetpay(APIKEY, SITEID)
    transaction_id = "".join(random.choices(string.digits, k=8))

    house_id = house.vn_house_id
    amount = house.vn_house_rent
    tenant = house.get_current_tenant()
    device = house.user_houses.vn_device

    data = {
        "amount": amount,
        "currency": device,
        "transaction_id": transaction_id,
        "description": f"Paiement du loyer {house_id}",
        "return_url": "https://g.venone.app/payment/success",
        "notify_url": "https://g.venone.app/payment/cancel",
        "customer_name": tenant,
        "customer_surname": tenant,
    }
    try:
        response = client.PaymentInitialization(data)
        payment_url = response["data"]["payment_url"]
        lg.warning(payment_url)
        if response["code"] == "201":
            VNHouse.record_payment(house, transaction_id)
        return payment_url
    except Exception as e:
        lg.warning(f"Error processing payment for house {house.vn_house_id}: {e}")
        return None

def send_sms_reminder(house, tenant):

    """Send an SMS reminder to the tenant to pay rent"""

    current_date = datetime.utcnow().date()
    app = current_app._get_current_object()

    SMS_API_KEY = app.config["SMS_API_KEY"]
    SMS_BASE_URL = app.config["SMS_BASE_URL"]
    SMS_SENDER_ID = app.config["SMS_SENDER_ID"]
    SMS_API_TOKEN = app.config["SMS_API_TOKEN"]

    house_payment_url = process_payment(house)
    s = pyshorteners.Shortener()
    short_url = s.dagd.short(house_payment_url)

    fullname = house.get_current_tenant()
    phone_number = house.get_tenant_phone_number()
    house_lease_end = house.vn_house_lease_end_date

    message = f"Bonjour {fullname}, votre facture de loyer\
    du mois de {house_lease_end} est prête.\
    Veuillez cliquer sur ce lien: {short_url} pour procéder au paiement. Merci, Venone."

    reqUrl = f"{SMS_BASE_URL}?sendsms&apikey={SMS_API_KEY}\
    &apitoken={SMS_API_TOKEN}&type=sms&from={SMS_SENDER_ID}&to={phone_number}&text={message}"

    if current_date == house_lease_end and not VNHouse.is_rent_paid(house):
        requests.request("POST", reqUrl)
