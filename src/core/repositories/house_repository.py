from src.core.mappers.house_mapper import HouseMapper
from src.core.repositories.base_repository import BaseRepository
from src.infrastructure.persistence.models import House, HouseOwner


class HouseRepository(BaseRepository):
    model = House
    mapper = HouseMapper

    def find_by_house_id(self, vn_house_id: str):
        return self.model.query.filter_by(vn_house_id=vn_house_id).first()

    def find_available_houses(self):
        return self.model.query.filter_by(vn_house_is_open=False)

    def find_expired_leases(self, current_date):
        records = self.model.query.filter(
            self.model.vn_house_is_open,  # noqa: E712
            self.model.vn_house_lease_end_date <= current_date,
        ).all()
        return [self.mapper.to_domain(r) for r in records]


class HouseOwnerRepository(BaseRepository):
    model = HouseOwner

    def find_by_owner_id(self, vn_owner_id: str):
        return self.model.query.filter_by(vn_owner_id=vn_owner_id).first()

    def find_by_user_id(self, user_id: int):
        return self.model.query.filter_by(vn_user_id=user_id).all()
