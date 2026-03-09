from src.core.domain.entities.stakeholders import OwnerEntity, TenantEntity
from src.infrastructure.persistence.models import HouseOwner, Tenant


class OwnerMapper:
    @staticmethod
    def to_domain(persistence: HouseOwner) -> OwnerEntity:
        return OwnerEntity(
            id=persistence.id,
            uuid=persistence.vn_owner_id,
            fullname=persistence.vn_fullname,
            phone=persistence.vn_phonenumber_one,
            owner_percent=persistence.vn_owner_percent,
            user_id=persistence.vn_user_id,
        )

    @staticmethod
    def to_persistence(entity: OwnerEntity) -> dict:
        return {
            "vn_fullname": entity.fullname,
            "vn_phonenumber_one": entity.phone,
            "vn_owner_percent": entity.owner_percent,
            "vn_user_id": entity.user_id,
        }


class TenantMapper:
    @staticmethod
    def to_domain(persistence: Tenant) -> TenantEntity:
        return TenantEntity(
            id=persistence.id,
            uuid=persistence.vn_tenant_id,
            fullname=persistence.vn_fullname,
            phone=persistence.vn_phonenumber_one,
            user_id=persistence.vn_user_id,
        )

    @staticmethod
    def to_persistence(entity: TenantEntity) -> dict:
        return {
            "vn_fullname": entity.fullname,
            "vn_phonenumber_one": entity.phone,
            "vn_user_id": entity.user_id,
        }
