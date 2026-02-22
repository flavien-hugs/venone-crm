import logging
from datetime import datetime

from flask import current_app, request
from flask_login import AnonymousUserMixin, UserMixin, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from src.constants import COUNTRY_DEFAULT
from src.exts import db, login_manager
from src.mixins.models import DefaultUserInfoModel, TimestampMixin
from src.tenant.models import VNHouse, VNHouseOwner, VNTenant

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Permission:
    ADMIN = 5
    STAFF = 7


class VNRole(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, index=True, primary_key=True)
    role_permissions = db.Column(db.Integer, default=Permission.ADMIN)
    role_name = db.Column(db.String(64), unique=True)
    role_default = db.Column(db.Boolean, default=False, index=True)
    users = db.relationship("VNUser", backref="role", lazy="dynamic")

    def __init__(self, **kwagrs):
        super(VNRole, self).__init__(**kwagrs)
        if self.role_permissions is None:
            self.role_permissions = 0

    def __repr__(self):
        return f"<User {self.role_name!r}>"

    def has_permission(self, perm):
        return self.role_permissions & perm == perm

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.role_permissions += perm

    def remove_permission(self, perm):
        if not self.has_permission(perm):
            self.role_permissions -= perm

    def reset_permission(self):
        self.role_permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            "Staff": [Permission.STAFF],
            "Administrateur": [0xFF],
        }
        default_role = "Administrateur"
        for r in roles:
            role = VNRole.query.filter_by(role_name=r).first()
            if role is None:
                role = VNRole(role_name=r)
                logger.info(f"Creating role: {r}")
            role.reset_permission()
            for perm in roles[r]:
                role.add_permission(perm)
            role.role_default = role.role_name == default_role
            db.session.add(role)
        db.session.commit()
        logger.info("Roles specialized successfully!")


class VNAgencieInfoModelMixin(db.Model):
    __abstract__ = True

    vn_agencie_name = db.Column(db.String(80), unique=True, nullable=True)
    vn_business_number = db.Column(db.String(80), unique=True, nullable=True)


class VNUser(
    UserMixin, DefaultUserInfoModel, VNAgencieInfoModelMixin, TimestampMixin, db.Model
):
    __tablename__ = "user"

    vn_country = db.Column(db.String(80), default=COUNTRY_DEFAULT, nullable=False)
    vn_avatar = db.Column(
        db.String(80), nullable=True, default="/static/img/element/avatar.png"
    )
    vn_password = db.Column(db.String(180), nullable=False)
    vn_birthdate = db.Column(db.Date, nullable=True)
    vn_last_seen = db.Column(db.DateTime, onupdate=datetime.utcnow())

    vn_house_owner = db.Column(db.Boolean(), default=False)
    vn_company = db.Column(db.Boolean(), default=False)

    vn_balance = db.Column(db.Float, nullable=True)

    vn_device = db.Column(db.String(80), nullable=True)
    vn_find_us = db.Column(db.String(100), nullable=True)
    vn_ip_address = db.Column(db.String(50), nullable=True)
    vn_role_id = db.Column(
        db.Integer, db.ForeignKey("roles.id", ondelete="SET NULL"), nullable=True
    )
    houseowners = db.relationship(
        "VNHouseOwner",
        backref="house_owner",
        lazy="dynamic",
        order_by="desc(VNHouseOwner.vn_created_at)",
    )
    houses = db.relationship(
        "VNHouse",
        lazy="dynamic",
        backref="user_houses",
        order_by="desc(VNHouse.vn_created_at)",
    )
    tenants = db.relationship(
        "VNTenant",
        lazy="dynamic",
        backref="user_tenants",
        order_by="desc(VNTenant.vn_created_at)",
    )
    payments = db.relationship(
        "VNPayment",
        lazy="dynamic",
        backref="user_payments",
        order_by="desc(VNPayment.vn_pay_date)",
    )
    transfers = db.relationship(
        "VNTransferRequest",
        lazy="dynamic",
        backref="user_transfer_requests",
        order_by="desc(VNTransferRequest.vn_created_at)",
    )
    percent = db.relationship("VNPercent", uselist=False, back_populates="user")

    def __str__(self):
        return self.vn_fullname or self.vn_agencie_name

    def __repr__(self) -> str:
        return f"VNUser(id={self.id!r}, fullname={self.vn_fullname!r})"

    def set_password(self, password):
        self.vn_password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.vn_password, password)

    def get_owner_percent(self) -> float:
        return getattr(self.percent, "vn_owner_percent", 7)

    def get_company_percent(self) -> float:
        return getattr(self.percent, "vn_company_percent", 6)

    def get_payments_list(self) -> list:
        payments = self.payments.filter_by(vn_payee_id=self.id, vn_pay_status=True)
        return payments

    def get_payments_count(self) -> int:
        payments_count = self.get_payments_list().count()
        return payments_count

    def get_houseowners_list(self) -> list:
        houseowners = self.houseowners.filter_by(vn_user_id=self.id)
        return houseowners

    def get_houseowners_count(self) -> int:
        houseowners_count = self.get_houseowners_list().count()
        return houseowners_count

    def get_transfers_list(self) -> list:
        transfers = self.transfers.filter_by(vn_user_id=self.id)
        return transfers

    def get_transfers_count(self) -> int:
        transfers_count = self.get_transfers_list().count()
        return transfers_count

    def get_houses_list(self) -> list:
        houses = self.houses.filter_by(vn_user_id=self.id)
        return houses

    def get_houses_count(self) -> int:
        houses_count = self.get_houses_list().count()
        return houses_count

    def get_houses_close_count(self) -> int:
        houses_close_count = self.houses.filter_by(
            vn_house_is_open=True, vn_user_id=self.id
        ).count()
        return houses_close_count

    def get_houses_open_count(self) -> int:
        houses_open_count = self.houses.filter_by(
            vn_house_is_open=False, vn_user_id=self.id
        ).count()
        return houses_open_count

    def get_tenants_list(self) -> list:
        tenants = self.tenants.filter_by(vn_user_id=self.id)
        return tenants

    def get_tenants_count(self) -> int:
        tenants_count = self.get_tenants_list().count()
        return tenants_count

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def disable(self):
        self.vn_activated = False
        db.session.commit()

    def ping(self):
        self.vn_ip_address = request.remote_addr
        self.vn_last_seen = datetime.utcnow()
        db.session.add(self)

    @classmethod
    def get_users_list(cls) -> list:
        users = cls.query.filter_by(vn_activated=True)
        return users

    @classmethod
    def get_companies_list(cls) -> list:
        companies = cls.query.filter_by(vn_company=True)
        return companies

    @classmethod
    def get_lessors_list(cls) -> list:
        lessors = cls.query.filter_by(vn_house_owner=True)
        return lessors

    @staticmethod
    def get_houses_by_country(page, per_page):
        user_country = current_user.vn_country
        pagination = (
            VNHouse.query.join(VNUser, VNHouse.vn_user_id == VNUser.id)
            .filter(not VNHouse.vn_house_is_open, VNUser.vn_country == user_country)
            .paginate(page=page, per_page=per_page)
        )

        user_houses = pagination.items
        return pagination, user_houses

    @classmethod
    def get_user_logged(cls) -> dict:
        user = cls.query.filter_by(id=current_user.id, vn_activated=True).first()
        return user

    def total_houses_amount(self):
        user_houses = self.houses.filter_by(
            vn_house_is_open=True, vn_user_id=self.id
        ).all()
        total = sum(house.vn_house_rent for house in user_houses)
        return total

    def total_houses_percent(self):
        if self.vn_house_owner:
            user_houses = self.houses.filter_by(
                vn_user_id=self.id, vn_house_is_open=True
            ).all()
            total_percent = sum(house.vn_house_rent for house in user_houses)
        elif self.vn_company:
            user_houses = (
                self.houses.filter_by(vn_house_is_open=True, vn_user_id=self.id)
                .join(VNHouseOwner)
                .filter(VNHouseOwner.vn_user_id.isnot(None))
                .all()
            )
            total_percent = sum(
                house.get_house_rent_with_percent() for house in user_houses
            )
        else:
            return 0

        return total_percent or 0

    @staticmethod
    def get_label(user):
        return user.get_name()

    def get_name(self):
        if self.vn_house_owner:
            return self.vn_fullname
        if self.vn_company:
            return self.vn_agencie_name

    @staticmethod
    def get_owner_per_month():
        count_by_month = (
            db.session.query(
                db.extract("year", VNHouseOwner.vn_created_at),
                db.extract("month", VNHouseOwner.vn_created_at),
                db.func.count(VNHouseOwner.id),
            )
            .join(VNUser, VNHouseOwner.vn_user_id == VNUser.id)
            .filter(VNUser.id == current_user.id)
            .group_by(
                db.extract("year", VNHouseOwner.vn_created_at),
                db.extract("month", VNHouseOwner.vn_created_at),
            )
            .all()
        )
        return count_by_month

    @staticmethod
    def get_tenant_per_month():
        count_by_month = (
            db.session.query(
                db.extract("year", VNTenant.vn_created_at),
                db.extract("month", VNTenant.vn_created_at),
                db.func.count(VNTenant.id),
            )
            .join(VNUser, VNTenant.vn_user_id == VNUser.id)
            .filter(VNUser.id == current_user.id)
            .group_by(
                db.extract("year", VNTenant.vn_created_at),
                db.extract("month", VNTenant.vn_created_at),
            )
            .all()
        )
        return count_by_month

    @staticmethod
    def get_trendprices():
        rent_prices = (
            db.session.query(
                db.extract("year", VNHouse.vn_created_at),
                db.extract("month", VNHouse.vn_created_at),
                db.func.avg(VNHouse.vn_house_rent),
            )
            .join(VNUser, VNHouse.vn_user_id == VNUser.id)
            .filter(VNUser.id == current_user.id)
            .group_by(
                db.extract("year", VNHouse.vn_created_at),
                db.extract("month", VNHouse.vn_created_at),
            )
            .all()
        )
        return rent_prices

    @staticmethod
    def houses_opened_count():
        houses_opened = (
            db.session.query(
                db.func.sum(
                    db.cast(
                        VNHouse.vn_house_is_open & (VNUser.id == current_user.id),
                        db.Integer,
                    )
                ),
                db.func.sum(
                    db.cast(
                        ~VNHouse.vn_house_is_open & (VNUser.id == current_user.id),
                        db.Integer,
                    )
                ),
            )
            .join(VNUser)
            .all()
        )

        return houses_opened

    def request_transfer(
        self, amount, withdrawal_number, withdrawal_method=None, cinetpay_data=None
    ):
        from src.payment import VNTransferRequest

        transfer = VNTransferRequest(
            vn_user_id=self.id,
            vn_trans_amount=amount,
            vn_withdrawal_number=withdrawal_number,
            vn_withdrawal_method=withdrawal_method,
            vn_cinetpay_data=cinetpay_data,
        )
        db.session.add(transfer)
        db.session.commit()

    def deduct_payments_received(self, amount):
        deduct = int(self.get_total_payments_received()) - int(amount)
        self.vn_balance = deduct
        db.session.commit()
        return self.vn_balance

    def get_total_payments_received(self):
        from src.payment import VNPayment
        from src.tenant import VNHouse, VNHouseOwner, VNTenant

        if self.vn_house_owner:
            total_payments = (
                db.session.query(db.func.sum(VNPayment.vn_pay_amount))
                .join(VNHouse)
                .join(VNTenant)
                .join(VNUser)
                .filter(
                    VNUser.uuid == self.uuid,
                    VNPayment.vn_pay_status,
                )
                .scalar()
            )
        elif self.vn_company:
            total_payments = (
                db.session.query(db.func.sum(VNPayment.vn_pay_amount))
                .join(VNHouse)
                .join(VNTenant)
                .join(VNHouseOwner)
                .join(VNUser)
                .filter(
                    VNUser.uuid == self.uuid,
                    VNPayment.vn_pay_status,
                )
                .scalar()
            )
        else:
            total_payments = 0

        self.vn_balance = total_payments
        db.session.commit()
        return total_payments or 0

    def total_payments_month(self):
        from src.payment import VNPayment
        from src.tenant import VNHouse, VNHouseOwner, VNTenant

        now = datetime.now()
        month = now.month
        year = now.year

        if self.vn_house_owner:
            total_payments = (
                db.session.query(db.func.sum(VNPayment.vn_pay_amount))
                .join(VNHouse)
                .join(VNTenant)
                .join(VNUser)
                .filter(
                    VNUser.uuid == self.uuid,
                    VNPayment.vn_pay_status,
                    db.extract("month", VNPayment.vn_pay_date) == month,
                    db.extract("year", VNPayment.vn_pay_date) == year,
                )
                .scalar()
            )
        elif self.vn_company:
            total_payments = (
                db.session.query(db.func.sum(VNPayment.vn_pay_amount))
                .join(VNHouse)
                .join(VNTenant)
                .join(VNHouseOwner)
                .join(VNUser)
                .filter(
                    VNUser.uuid == self.uuid,
                    VNPayment.vn_pay_status,
                    db.extract("month", VNPayment.vn_pay_date) == month,
                    db.extract("year", VNPayment.vn_pay_date) == year,
                )
                .scalar()
            )
        else:
            return 0
        return total_payments or 0

    def amount_apply_percent(self):
        if self.vn_house_owner:
            percent = self.get_owner_percent() / 100
            houses = self.houses.filter_by(vn_house_is_open=True).all()
            total_percents = sum((house.vn_house_rent * percent) for house in houses)
        elif self.vn_company:
            percent = self.get_company_percent() / 100
            houses = (
                self.houses.join(VNHouseOwner)
                .filter(VNHouseOwner.vn_user_id == self.id, VNHouse.vn_house_is_open)
                .all()
            )
            total_percents = sum(
                (house.get_house_rent_with_percent() * percent) for house in houses
            )
        else:
            return 0
        return total_percents or 0

    def get_amount_received(self):
        return self.total_houses_percent() - self.amount_apply_percent()

    @staticmethod
    def create_admin():
        """
        Create the admin user.
        """
        addr_email = current_app.config["ADMIN_EMAIL"]
        fullname = current_app.config["ADMIN_USERNAME"]
        password = current_app.config["ADMIN_PASSWORD"]
        phonenumber_one = current_app.config["ADMIN_PHONE_NUMBER"]

        try:
            user = VNUser(vn_addr_email=addr_email)
            user.vn_fullname = fullname
            user.vn_password = generate_password_hash(password)
            user.vn_phonenumber_one = phonenumber_one

            # Look up Administrateur role instead of hardcoding ID 5
            admin_role = VNRole.query.filter_by(role_name="Administrateur").first()
            if admin_role:
                user.vn_role_id = admin_role.id
            else:
                logger.warning(
                    "Administrateur role not found, defaulting to Permission.ADMIN value"
                )
                user.vn_role_id = Permission.ADMIN

            db.session.add(user)
            db.session.commit()
            logger.info(f"Admin with email {addr_email} created successfully!")
        except Exception as e:
            logger.warning(f"Couldn't create admin user, because {e}")


class VNPercent(TimestampMixin):
    __tablename__ = "percent"

    vn_user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    user = db.relationship("VNUser", back_populates="percent")
    vn_owner_percent = db.Column(db.Float, default=7, nullable=True)
    vn_company_percent = db.Column(db.Float, default=6, nullable=True)

    def __init__(self, user, vn_owner_percent=7, vn_company_percent=6):
        self.user = user
        self.vn_owner_percent = vn_owner_percent
        self.vn_company_percent = vn_company_percent

    def __str__(self):
        return self.user

    def __repr__(self):
        return f"VNPercent({self.id}, {self.owner_percent}, {self.company_percent})"


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(VNUser).get(user_id)
