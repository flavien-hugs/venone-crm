import logging
from cinetpay_sdk.s_d_k import Cinetpay

from src.core.interfaces.payment_provider import IPaymentProvider

logger = logging.getLogger(__name__)


class CinetPayProvider(IPaymentProvider):
    def __init__(self, api_key: str, site_id: str):
        self.client = Cinetpay(api_key, site_id)

    def verify_transaction(self, transaction_id: str) -> dict:
        try:
            response = self.client.TransactionVerfication_trx(transaction_id)
            if response and isinstance(response, dict):
                code = response.get("code")
                data = response.get("data", {})
                status = data.get("status")

                # Normalize response for the internal system
                if code == "00" and status == "ACCEPTED":
                    internal_status = "SUCCESS"
                elif code == "662" and status == "PENDING":
                    internal_status = "PENDING"
                else:
                    internal_status = "FAILED"

                return {
                    "status": internal_status,
                    "code": code,
                    "raw_response": response,
                    "message": response.get("message", ""),
                }
            return {"status": "FAILED", "message": "Invalid response from CinetPay"}
        except Exception as e:
            logger.error(
                f"Error verifying transaction {transaction_id} with CinetPay: {e}"
            )
            return {"status": "ERROR", "message": str(e)}

    def initiate_payment(
        self,
        amount: float,
        currency: str,
        transaction_id: str,
        description: str,
        customer_name: str,
        customer_surname: str,
    ) -> dict:
        data = {
            "amount": amount,
            "currency": currency,
            "transaction_id": transaction_id,
            "description": description,
            "return_url": "https://g.venone.app/payment/success",
            "notify_url": "https://g.venone.app/payment/cancel",
            "customer_name": customer_name,
            "customer_surname": customer_surname,
        }
        try:
            response = self.client.PaymentInitialization(data)
            logger.info(f"Payment initialization response: {response}")
            return response
        except Exception as e:
            logger.error(
                f"Error initiating payment {transaction_id} with CinetPay: {e}"
            )
            return {"code": "-1", "message": str(e)}
