import json
import logging

import requests
from cinetpay_sdk.s_d_k import Cinetpay
from flask import current_app
from src.exts import db

from .models import VNPayment
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def check_transaction_trx():
    try:
        current_app_obj = current_app._get_current_object()
        SITEID = current_app_obj.config.get("CINETPAY_SITE_ID")
        APIKEY = current_app_obj.config.get("CINETPAY_API_KEY")
        client = Cinetpay(APIKEY, SITEID)

        payments = VNPayment.unpaids()

        for payment in payments:
            logger.info("Payment transaction ID: %s", payment.vn_transaction_id)
            response = client.TransactionVerfication_trx(payment.vn_transaction_id)

            if response and isinstance(response, dict):
                try:
                    logger.info("Response data: %s", type(response))

                    code = response.get("code")
                    status = response.get("data", {}).get("status")

                    if code == "00" and status == "ACCEPTED":
                        payment.vn_pay_status = True
                    elif code == "662" and status == "PENDING":
                        payment.vn_pay_status = False
                    else:
                        logger.warning(
                            "Invalid response data for transaction ID %s: %s",
                            payment.vn_transaction_id,
                        )
                    payment.vn_cinetpay_data = json.dumps(response)
                    db.session.commit()
                except json.JSONDecodeError as json_error:
                    logger.error(
                        "Error decoding JSON response for transaction ID %s: %s",
                        payment.vn_transaction_id,
                        response.text,
                    )
                    payment.vn_pay_status = False
                    logger.error(
                        "JSON decoding error for transaction ID %s: %s",
                        payment.vn_transaction_id,
                        json_error,
                    )
                    db.session.commit()
            else:
                logger.warning(
                    "Invalid response for transaction ID %s: %s",
                    payment.vn_transaction_id,
                    response.text,
                )
    except requests.exceptions.RequestException as req_error:
        logger.error("Error in request: %s", req_error)
        raise req_error
    except Exception as e:
        logger.exception("Error transaction: %s", e)
        raise e
