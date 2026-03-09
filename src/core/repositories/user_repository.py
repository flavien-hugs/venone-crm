from typing import Optional

from src.core.domain.entities.user import UserEntity
from src.core.mappers.user_mapper import UserMapper
from src.core.repositories.base_repository import BaseRepository
from src.infrastructure.persistence.models import (
    House,
    HouseOwner,
    Payment,
    Tenant,
    TransferRequest,
)
from src.infrastructure.persistence.models import User


class UserRepository(BaseRepository):
    model = User
    mapper = UserMapper

    def get_by_id(self, id: int) -> Optional[UserEntity]:
        record = self.model.query.get(id)
        return self.mapper.to_domain(record) if record else None

    def get_payments_list(self, user_id: int):
        return Payment.query.filter_by(vn_payee_id=user_id).order_by(
            Payment.vn_created_at.desc()
        )

    def get_houses_list(self, user_id: int):
        return House.query.filter_by(vn_user_id=user_id).order_by(
            House.vn_created_at.desc()
        )

    def get_tenants_list(self, user_id: int):
        return Tenant.query.filter_by(vn_user_id=user_id).order_by(
            Tenant.vn_created_at.desc()
        )

    def get_owners_list(self, user_id: int):
        return HouseOwner.query.filter_by(vn_user_id=user_id).order_by(
            HouseOwner.vn_created_at.desc()
        )

    def get_transfers_list(self, user_id: int):
        return (
            TransferRequest.query.filter_by(vn_user_id=user_id)
            .order_by(TransferRequest.vn_created_at.desc())
            .all()
        )

    def get_transfers_request(self, user_id: int):
        return TransferRequest.query.filter_by(vn_user_id=user_id)

    def get_houses_by_country(self, country: str):
        return House.query.join(self.model).filter(self.model.vn_country == country)

    def find_by_uuid(self, uuid: str) -> Optional[UserEntity]:
        record = self.model.query.filter_by(uuid=uuid).first()
        return self.mapper.to_domain(record) if record else None
