from src.core.domain.entities.house import HouseEntity
from src.infrastructure.persistence.models import House


class HouseMapper:
    @staticmethod
    def to_domain(persistence: House) -> HouseEntity:
        return HouseEntity(
            id=persistence.id,
            uuid=persistence.vn_house_id,
            type=persistence.vn_house_type,
            rent=persistence.vn_house_rent,
            is_open=persistence.vn_house_is_open,
            lease_end_date=persistence.vn_house_lease_end_date,
            user_id=persistence.vn_user_id,
            owner_id=persistence.vn_owner_id,
        )

    @staticmethod
    def to_persistence(entity: HouseEntity) -> dict:
        return {
            "vn_house_type": entity.type,
            "vn_house_rent": entity.rent,
            "vn_house_is_open": entity.is_open,
            "vn_house_lease_end_date": entity.lease_end_date,
            "vn_user_id": entity.user_id,
            "vn_owner_id": entity.owner_id,
        }
