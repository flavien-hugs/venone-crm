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
            response_data = client.TransactionVerfication_trx(payment.vn_transaction_id)
            logger.info("response data: %s", response_data)

            if isinstance(response_data, dict):
                if (
                    response_data["code"] == "00"
                    and response_data["data"]["status"] == "ACCEPTED"
                ):
                    payment.vn_pay_status = True
                    payment.vn_cinetpay_data = response_data
                    db.session.commit()
                elif (
                    response_data["code"] == "662"
                    and response_data["message"] == "WAITING_CUSTOMER_PAYMENT"
                    and response_data["data"]["status"] == "PENDING"
                ):
                    payment.vn_pay_status = False
                    payment.vn_cinetpay_data = response_data
                    db.session.commit()
                else:
                    logger.warning(
                        "Invalid response data for transaction ID %s: %s",
                        payment.id,
                        response_data,
                    )
            else:
                logger.warning(
                    "Invalid response data type for transaction ID %s: %s",
                    payment.id,
                    type(response_data),
                )
    except Exception as e:
        logger.warning("Error processing transaction: %s", e)
