import secrets
import logging as lg
from datetime import datetime

import requests
import pyshorteners
from flask import current_app
from src.tenant import VNHouse
from cinetpay_sdk.s_d_k import Cinetpay


def run_process_payment(house):
    app = current_app._get_current_object()
    SITEID = app.config["CINETPAY_SITE_ID"]
    APIKEY = app.config["CINETPAY_API_KEY"]

    client = Cinetpay(APIKEY, SITEID)
    transaction_id = secrets.randbelow(10**8)

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
        lg.info(f"Response data : {response}")
        if response["code"] == "201":
            VNHouse.process_payment_data(house, transaction_id)
            return response["data"]["payment_url"]
        else:
            lg.warning(
                f"Error processing payment for house {house.vn_house_id}: {response['message']}"
            )
            return None
    except Exception as e:
        lg.warning(f"Error processing payment for house {house.vn_house_id}: {e}")
        raise e


def send_sms_reminder(house, tenant):
    current_date = datetime.utcnow().date()
    app = current_app._get_current_object()

    SMS_API_KEY = app.config["SMS_API_KEY"]
    SMS_BASE_URL = app.config["SMS_BASE_URL"]
    SMS_SENDER_ID = app.config["SMS_SENDER_ID"]
    SMS_API_TOKEN = app.config["SMS_API_TOKEN"]

    house_payment_url = run_process_payment(house)
    if house_payment_url is None:
        lg.warning(
            f"Payment URL is None for house {house.vn_house_id}. SMS reminder not sent."
        )
        return

    s = pyshorteners.Shortener()
    short_url = s.dagd.short(house_payment_url)

    fullname = house.get_current_tenant()
    phone_number = house.get_tenant_phone_number()
    house_lease_end = house.vn_house_lease_end_date

    message = f"Bonjour {fullname}, votre loyer\
    du mois de {house_lease_end} est prête.\
    Veuillez cliquer sur ce lien: {short_url} pour procéder au paiement. Merci, Venone."

    if current_date == house_lease_end and not house.is_rent_paid(tenant_id=tenant.id):
        reqUrl = f"{SMS_BASE_URL}?sendsms&apikey={SMS_API_KEY}&apitoken={SMS_API_TOKEN}\
        &type=sms&from={SMS_SENDER_ID}&to={phone_number}&text={message}"

        try:
            requests.request("POST", reqUrl)
            if reqUrl is not None and not reqUrl.startswith(("http://", "https://")):
                lg.info(
                    f"SMS reminder sent to {phone_number} for house {house.vn_house_id}"
                )
            else:
                lg.warning(f"Failed to send SMS reminder for house {house.vn_house_id}")
        except Exception as e:
            lg.warning(f"Error sending SMS reminder for house {house.vn_house_id}: {e}")
    else:
        lg.info(f"No SMS reminder sent for house {house.vn_house_id}")
