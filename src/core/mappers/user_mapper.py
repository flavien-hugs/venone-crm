from src.infrastructure.persistence.models import User
from src.core.domain.entities.user import UserEntity


class UserMapper:
    @staticmethod
    def to_domain(persistence: User) -> UserEntity:
        return UserEntity(
            id=persistence.id,
            uuid=persistence.uuid or "",
            fullname=persistence.vn_fullname,
            email=persistence.vn_addr_email,
            phone=persistence.vn_phonenumber_one,
            country=persistence.vn_country,  # Optional[str]
            balance=persistence.vn_balance or 0.0,
            is_house_owner=bool(persistence.vn_house_owner),  # None -> False
            is_company=bool(persistence.vn_company),  # None -> False
            is_administrator=persistence.is_administrator(),
            owner_percent=persistence.get_owner_percent(),
            company_percent=persistence.get_company_percent(),
        )

    @staticmethod
    def to_persistence(entity: UserEntity) -> dict:
        return {
            "vn_fullname": entity.fullname,
            "vn_addr_email": entity.email,
            "vn_phonenumber_one": entity.phone,
            "vn_country": entity.country,
            "vn_balance": entity.balance,
            "vn_house_owner": entity.is_house_owner,
            "vn_company": entity.is_company,
        }
