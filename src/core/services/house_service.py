import logging
from datetime import datetime, timedelta
from typing import Optional

from src.core.repositories.house_repository import HouseOwnerRepository, HouseRepository
from src.core.repositories.tenant_repository import TenantRepository
from src.infrastructure.config.plugins import db
from src.infrastructure.persistence.models import Payment, Tenant

logger = logging.getLogger(__name__)


class HouseService:
    def __init__(self, house_repo: HouseRepository, owner_repo: HouseOwnerRepository):
        self.house_repo = house_repo
        self.owner_repo = owner_repo

    def update_lease_end_date_if_expired(self, house_id: int):
        house = self.house_repo.model.query.get(house_id)
        if not house:
            return

        current_date = datetime.utcnow().date()
        if house.vn_house_lease_end_date <= current_date:
            # Shift the date by 1 month
            house.vn_house_lease_end_date += timedelta(days=30)
            db.session.commit()
            logger.info(f"Updated lease end date for house {house_id}")

    def request_transfer(self, user_id: int, amount: float):
        # Placeholder - real logic in UserService
        pass

    def calculate_company_revenue_from_house(self, house_id: int) -> float:
        house = self.house_repo.get_by_id(house_id)
        if not house or not house.owner_id:
            return 0.0

        owner = self.owner_repo.get_by_id(house.owner_id)
        if owner and hasattr(owner, "owner_percent") and owner.owner_percent:
            percent = owner.owner_percent / 100
            return house.rent * percent
        return 0.0

    def get_status_label(self, house_id: int) -> str:
        house = self.house_repo.model.query.get(house_id)
        if not house:
            return "N/A"
        return "Occupée" if house.vn_house_is_open else "Libre"

    def get_current_tenant_id(self, house_id: int) -> Optional[int]:
        tenant = (
            Tenant.query.filter_by(vn_house_id=house_id)
            .order_by(db.desc("vn_created_at"))
            .first()
        )
        return tenant.id if tenant else None

    def get_tenant_phone_number(self, house_id: int) -> Optional[str]:
        tenant = (
            Tenant.query.filter_by(vn_house_id=house_id)
            .order_by(db.desc("vn_created_at"))
            .first()
        )
        return tenant.vn_phonenumber_one if tenant else None


class TenantService:
    def __init__(self, tenant_repo: TenantRepository):
        self.tenant_repo = tenant_repo

    def is_rent_paid_this_month(self, tenant_id: int, house_id: int) -> bool:
        current_date = datetime.utcnow().date()
        current_year = current_date.year
        current_month = current_date.month

        query = Payment.query.filter(
            Payment.vn_pay_status,
            Payment.vn_tenant_id == tenant_id,
            Payment.vn_house_id == house_id,
            db.extract("month", Payment.vn_pay_date) == current_month,
            db.extract("year", Payment.vn_pay_date) == current_year,
        )
        return query.count() > 0
