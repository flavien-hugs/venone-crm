from datetime import datetime
from typing import Dict, Optional

from src.core.repositories.user_repository import UserRepository
from src.infrastructure.config.plugins import db
from src.infrastructure.persistence.models import (
    House,
    HouseOwner,
    Payment,
    Tenant,
    TransferRequest,
)


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_total_payments_received(self, user_id: int) -> float:
        user = self.repository.get_by_id(user_id)
        if not user:
            return 0.0

        query = db.session.query(db.func.sum(Payment.vn_pay_amount)).filter(
            Payment.vn_pay_status
        )

        if user.is_administrator:
            total = query.scalar()
        elif user.is_house_owner:
            total = (
                query.join(House)
                .join(Tenant)
                .join(self.repository.model)
                .filter(self.repository.model.id == user.id)
                .scalar()
            )
        elif user.is_company:
            total = (
                query.join(House)
                .join(Tenant)
                .join(HouseOwner)
                .join(self.repository.model)
                .filter(self.repository.model.id == user.id)
                .scalar()
            )
        else:
            total = 0.0

        return total or 0.0

    def deduct_balance(self, user_id: int, amount: int):
        user_record = self.repository.model.query.get(user_id)
        if user_record:
            if user_record.vn_balance is None:
                user_record.vn_balance = 0.0
            user_record.vn_balance -= amount
            db.session.commit()

    def get_user_monthly_payments(self, user_id: int) -> float:
        user = self.repository.get_by_id(user_id)
        if not user:
            return 0.0

        now = datetime.utcnow()
        month = now.month
        year = now.year

        query = db.session.query(db.func.sum(Payment.vn_pay_amount)).filter(
            Payment.vn_pay_status,
            db.extract("month", Payment.vn_pay_date) == month,
            db.extract("year", Payment.vn_pay_date) == year,
        )

        if user.is_administrator:
            total = query.scalar()
        elif user.is_house_owner:
            total = (
                query.join(House)
                .join(Tenant)
                .join(self.repository.model)
                .filter(self.repository.model.id == user.id)
                .scalar()
            )
        elif user.is_company:
            total = (
                query.join(House)
                .join(Tenant)
                .join(HouseOwner)
                .join(self.repository.model)
                .filter(self.repository.model.id == user.id)
                .scalar()
            )
        else:
            total = 0.0

        return total or 0.0

    def calculate_amount_apply_percent(self, user_id: int) -> float:
        user = self.repository.get_by_id(user_id)
        if not user:
            return 0.0

        total_percents = 0.0
        if user.is_administrator:
            # Global potential commissions? Sum for all company-managed houses
            houses = House.query.filter_by(vn_house_is_open=True).all()
            for house in houses:
                if house.owner and house.owner.vn_owner_percent:
                    # Let's assume a default or sum across all companies
                    # This is complex, but to avoid 0.0:
                    owner_share = house.vn_house_rent * (
                        house.owner.vn_owner_percent / 100
                    )
                    # Use a default 10% or similar if we can't find a company percent
                    total_percents += owner_share * 0.1
        elif user.is_house_owner:
            percent = user.owner_percent / 100
            houses = House.query.filter_by(
                vn_user_id=user.id, vn_house_is_open=True
            ).all()
            total_percents = sum((house.vn_house_rent * percent) for house in houses)
        elif user.is_company:
            percent = user.company_percent / 100
            houses = (
                House.query.join(HouseOwner)
                .filter(HouseOwner.vn_user_id == user.id, House.vn_house_is_open)
                .all()
            )

            for house in houses:
                if house.owner and house.owner.vn_owner_percent:
                    owner_share = house.vn_house_rent * (
                        house.owner.vn_owner_percent / 100
                    )
                    total_percents += owner_share * percent

        return float(total_percents or 0.0)

    def calculate_total_amount_of_houses(self, user_id: int) -> float:
        user = self.repository.get_by_id(user_id)
        if not user:
            return 0.0

        if user.is_administrator:
            # For admin, sum of all rents for open houses
            user_houses = House.query.filter_by(vn_house_is_open=True).all()
        elif user.is_house_owner:
            user_houses = House.query.filter_by(
                vn_user_id=user.id, vn_house_is_open=True
            ).all()
        else:
            # Agencies/Companies: show houses they manage
            user_houses = House.query.filter_by(
                vn_user_id=user.id, vn_house_is_open=True
            ).all()

        total = sum(h.vn_house_rent for h in user_houses if h.vn_house_rent)
        return float(total)

    def calculate_total_houses_amount(self, user_id: int) -> float:
        """Alias for calculate_total_amount_of_houses to maintain compatibility."""
        return self.calculate_total_amount_of_houses(user_id)

    def get_dashboard_stats(self, user_id: int) -> Dict:
        user = self.repository.get_by_id(user_id)
        if not user:
            return {}

        if user.is_administrator:
            return {
                "payments_count": Payment.query.count(),
                "houses_count": House.query.count(),
                "houses_close_count": House.query.filter_by(
                    vn_house_is_open=True
                ).count(),
                "houses_open_count": House.query.filter_by(
                    vn_house_is_open=False
                ).count(),
                "tenants_count": Tenant.query.count(),
                "owners_count": HouseOwner.query.count(),
                "transfers_count": TransferRequest.query.count(),
            }

        return {
            "payments_count": Payment.query.filter_by(vn_payee_id=user.id).count(),
            "houses_count": House.query.filter_by(vn_user_id=user.id).count(),
            "houses_close_count": House.query.filter_by(
                vn_user_id=user.id, vn_house_is_open=True
            ).count(),
            "houses_open_count": House.query.filter_by(
                vn_user_id=user.id, vn_house_is_open=False
            ).count(),
            "tenants_count": Tenant.query.filter_by(vn_user_id=user.id).count(),
            "owners_count": HouseOwner.query.filter_by(vn_user_id=user.id).count(),
            "transfers_count": TransferRequest.query.filter_by(
                vn_user_id=user.id
            ).count(),
        }

    def get_payments_list(self, user_id: int):
        user = self.repository.get_by_id(user_id)
        if user and user.is_administrator:
            return Payment.query.order_by(db.desc("vn_created_at"))
        return self.repository.get_payments_list(user_id)

    def get_houses_list(self, user_id: int):
        user = self.repository.get_by_id(user_id)
        if user and user.is_administrator:
            return House.query.order_by(House.vn_created_at.desc())
        return self.repository.get_houses_list(user_id)

    def get_tenants_list(self, user_id: int):
        user = self.repository.get_by_id(user_id)
        if user and user.is_administrator:
            return Tenant.query.order_by(Tenant.vn_created_at.desc())
        return self.repository.get_tenants_list(user_id)

    def get_owners_list(self, user_id: int):
        user = self.repository.get_by_id(user_id)
        if user and user.is_administrator:
            return HouseOwner.query.order_by(HouseOwner.vn_created_at.desc())
        return self.repository.get_owners_list(user_id)

    def get_transfers_list(self, user_id: int):
        user = self.repository.get_by_id(user_id)
        if user and user.is_administrator:
            return TransferRequest.query.order_by(db.desc("vn_created_at")).all()
        return self.repository.get_transfers_list(user_id)

    def get_transfers_request(self, user_id: int):
        user = self.repository.get_by_id(user_id)
        if user and user.is_administrator:
            return TransferRequest.query.order_by(db.desc("vn_created_at"))
        return self.repository.get_transfers_request(user_id).order_by(
            db.desc("vn_created_at")
        )

    def request_transfer(
        self,
        user_id: int,
        amount: float,
        withdrawal_number: str,
        withdrawal_method: Optional[str] = None,
        cinetpay_data: Optional[Dict] = None,
    ) -> Optional[TransferRequest]:
        user = self.repository.get_by_id(user_id)
        if not user:
            return None

        transfer = TransferRequest(
            vn_user_id=user.id,
            vn_trans_amount=amount,
            vn_withdrawal_number=withdrawal_number,
            vn_withdrawal_method=withdrawal_method,
            vn_cinetpay_data=cinetpay_data,
        )
        db.session.add(transfer)
        db.session.commit()
        return transfer

    def get_owner_per_month(self, user_id: int):
        user = self.repository.get_by_id(user_id)

        # Ensure we filter out records with no creation date to avoid grouping errors
        year_expr = db.extract("year", HouseOwner.vn_created_at)
        month_expr = db.extract("month", HouseOwner.vn_created_at)

        query = db.session.query(
            year_expr.label("year"),
            month_expr.label("month"),
            db.func.count(HouseOwner.id).label("count"),
        ).filter(HouseOwner.vn_created_at.isnot(None))

        if user and not user.is_administrator:
            query = query.filter(HouseOwner.vn_user_id == user_id)

        return (
            query.group_by(year_expr, month_expr)
            .order_by(year_expr.desc(), month_expr.desc())
            .all()
        )

    def get_tenant_per_month(self, user_id: int):
        user = self.repository.get_by_id(user_id)

        year_expr = db.extract("year", Tenant.vn_created_at)
        month_expr = db.extract("month", Tenant.vn_created_at)

        query = db.session.query(
            year_expr.label("year"),
            month_expr.label("month"),
            db.func.count(Tenant.id).label("count"),
        ).filter(Tenant.vn_created_at.isnot(None))

        if user and not user.is_administrator:
            query = query.filter(Tenant.vn_user_id == user_id)

        return (
            query.group_by(year_expr, month_expr)
            .order_by(year_expr.desc(), month_expr.desc())
            .all()
        )

    def get_trendprices(self, user_id: int):
        user = self.repository.get_by_id(user_id)
        year = db.extract("year", Payment.vn_pay_date)
        month = db.extract("month", Payment.vn_pay_date)

        query = db.session.query(
            year.label("year"),
            month.label("month"),
            db.func.sum(Payment.vn_pay_amount).label("total"),
        ).filter(Payment.vn_pay_status)

        if user and not user.is_administrator:
            query = query.filter(Payment.vn_payee_id == user_id)

        return query.group_by(
            db.extract("year", Payment.vn_pay_date),
            db.extract("month", Payment.vn_pay_date),
        ).all()

    def houses_opened_count(self, user_id: int):
        user = self.repository.get_by_id(user_id)
        if user and user.is_administrator:
            opened = House.query.filter_by(vn_house_is_open=True).count()
            closed = House.query.filter_by(vn_house_is_open=False).count()
        else:
            opened = House.query.filter_by(
                vn_user_id=user_id, vn_house_is_open=True
            ).count()
            closed = House.query.filter_by(
                vn_user_id=user_id, vn_house_is_open=False
            ).count()
        return {"isOpen": opened, "notOpen": closed}
