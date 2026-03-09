from src.core.domain.entities.payment import PaymentEntity
from src.infrastructure.persistence.models import Payment


class PaymentMapper:
    @staticmethod
    def to_domain(persistence: Payment) -> PaymentEntity:
        return PaymentEntity(
            id=persistence.id,
            transaction_id=persistence.vn_transaction_id,
            amount=persistence.vn_pay_amount,
            status=persistence.vn_pay_status,
            date=persistence.vn_pay_date,
            house_id=persistence.vn_house_id,
            tenant_id=persistence.vn_tenant_id,
            owner_id=persistence.vn_owner_id,
            cinetpay_data=persistence.vn_cinetpay_data,
        )

    @staticmethod
    def to_persistence(entity: PaymentEntity) -> dict:
        return {
            "vn_transaction_id": entity.transaction_id,
            "vn_pay_amount": entity.amount,
            "vn_pay_status": entity.status,
            "vn_pay_date": entity.date,
            "vn_house_id": entity.house_id,
            "vn_tenant_id": entity.tenant_id,
            "vn_owner_id": entity.owner_id,
            "vn_cinetpay_data": entity.cinetpay_data,
        }
