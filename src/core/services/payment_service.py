import logging
import secrets
from datetime import datetime
from typing import Optional

from src.core.interfaces.payment_provider import IPaymentProvider
from src.core.repositories.payment_repository import PaymentRepository
from src.infrastructure.config.plugins import db
from src.infrastructure.persistence.models import Payment, Tenant

logger = logging.getLogger(__name__)


class PaymentService:
    def __init__(
        self, repository: PaymentRepository, provider: Optional[IPaymentProvider] = None
    ):
        self.repository = repository
        self.provider = provider

    def verify_payment_with_provider(self, transaction_id: str):
        if not self.provider:
            logger.warning("No payment provider configured for verification.")
            return

        payment = self.repository.find_by_transaction_id(transaction_id)
        if not payment:
            return

        result = self.provider.verify_transaction(transaction_id)
        if result["status"] == "SUCCESS":
            payment.vn_pay_status = True
            db.session.commit()
            logger.info(f"Transaction {transaction_id} verified as SUCCESS")
        elif result["status"] == "FAILED":
            logger.warning(f"Transaction {transaction_id} verification FAILED")
        else:
            logger.debug(f"Transaction {transaction_id} status: {result['status']}")

    def verify_all_pending_payments(self):
        # Implementation could use repo to find pending payments
        pass

    def initiate_payment_url(self, house_model) -> Optional[str]:
        if not self.provider:
            logger.error("No payment provider configured for initiation.")
            return None

        from src.core import get_house_service  # Moved import

        transaction_id = str(secrets.randbelow(10**8))
        house_service = get_house_service()

        tenant_id = house_service.get_current_tenant_id(house_model.id)
        tenant_obj = Tenant.query.get(tenant_id) if tenant_id else None
        tenant_name = tenant_obj.vn_fullname if tenant_obj else "Locataire"

        device = house_model.user_houses.vn_device or "XOF"

        response = self.provider.initiate_payment(
            amount=house_model.vn_house_rent,
            currency=device,
            transaction_id=transaction_id,
            description=f"Paiement du loyer {house_model.vn_house_id}",
            customer_name=tenant_name,
            customer_surname=tenant_name,
        )

        if response.get("code") == "201":
            self.process_payment_data(house_model.id, transaction_id)
            return response["data"]["payment_url"]
        else:
            logger.warning(f"Error initiating payment: {response.get('message')}")
            return None

    def process_payment_data(self, house_id: int, transaction_id: str):
        from src.core import get_house_service  # Moved import

        house_service = get_house_service()
        house = house_service.house_repo.model.query.get(house_id)

        if house and house.vn_house_is_open:
            payment = Payment(
                vn_transaction_id=transaction_id,
                vn_pay_amount=house.vn_house_rent,
                vn_payee_id=house.vn_user_id,
                vn_pay_date=datetime.utcnow().date(),
                vn_pay_status=True,  # Assuming success since URL was generated
                vn_house_id=house.id,
                vn_tenant_id=house_service.get_current_tenant_id(house.id),
                vn_owner_id=house.vn_owner_id,
            )
            db.session.add(payment)
            db.session.commit()
            return payment
        return None
