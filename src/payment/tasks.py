import json
import logging

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
        SITEID = current_app_obj.config["CINETPAY_SITE_ID"]
        APIKEY = current_app_obj.config["CINETPAY_API_KEY"]
        client = Cinetpay(APIKEY, SITEID)

        payments = VNPayment.unpaids()

        for payment in payments:
            logger.info("payment transaction ID: %s", payment.vn_transaction_id)
            response_data = client.TransactionVerfication_trx(payment.vn_transaction_id)
            logger.info("response data: %s", response_data)

            if isinstance(response_data, dict):
                try:
                    code = response_data.get("code")
                    status = response_data.get("data", {}).get("status")

                    if code == "00" and status == "ACCEPTED":
                        payment.vn_pay_status = True
                    elif code == "662" and status == "PENDING":
                        payment.vn_pay_status = False
                    else:
                        logger.warning(
                            "Invalid response data for transaction ID %s: %s",
                            payment.vn_transaction_id,
                            response_data,
                        )

                    payment.vn_cinetpay_data = response_data
                    db.session.commit()
                except json.JSONDecodeError as e:
                    logger.warning(
                        "Error decoding JSON response for transaction ID %s: %s",
                        payment.vn_transaction_id,
                        response_data,
                    )
            else:
                logger.warning(
                    "Empty response data for transaction ID %s",
                    payment.vn_transaction_id,
                )
    except Exception as e:
        logger.exception("Error processing transaction: %s", e)
