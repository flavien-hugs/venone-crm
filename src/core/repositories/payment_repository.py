from src.core.repositories.base_repository import BaseRepository
from src.infrastructure.config.plugins import db
from src.infrastructure.persistence.models import Payment


class PaymentRepository(BaseRepository):
    model = Payment

    def find_paids(self, user_id: int):
        return self.model.query.filter_by(
            vn_payee_id=user_id, vn_pay_status=True
        ).order_by(self.model.vn_created_at.desc())

    def find_all_ordered(self):
        return db.select(self.model).order_by(self.model.vn_created_at.desc())

    def find_unpaids(self):
        return self.model.query.filter_by(vn_pay_status=False).order_by(
            self.model.vn_created_at.desc()
        )

    def find_by_transaction_id(self, transaction_id):
        return self.model.query.filter_by(vn_transaction_id=transaction_id).first()
