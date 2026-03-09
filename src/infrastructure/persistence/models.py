import logging
from datetime import datetime

from flask import current_app
from flask_login import AnonymousUserMixin, UserMixin, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from src.infrastructure.shared.constants import COUNTRY_DEFAULT
from src.infrastructure.config.plugins import db, login_manager
from src.infrastructure.persistence.mixins import (
    DefaultUserInfoModel,
    TimestampMixin,
    id_generator,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Permission:
    """
    Permissions are defined as powers of 2, allowing for bitwise operations
    to combine and check for multiple permissions.
    """
    LOGIN = 1
    MANAGE_HOUSES = 2
    MANAGE_TENANTS = 4
    MANAGE_PAYMENTS = 8
    MANAGE_USERS = 16
    ADMIN = 128  # A separate high-level permission


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, index=True, primary_key=True)
    role_permissions = db.Column(db.Integer, default=0)
    role_name = db.Column(db.String(64), unique=True)
    role_default = db.Column(db.Boolean, default=False, index=True)
    users = db.relationship("User", backref="role", lazy="dynamic")

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.role_permissions is None:
            self.role_permissions = 0

    def __repr__(self):
        return f"<Role {self.role_name!r}>"

    def has_permission(self, perm):
        """Check if the role has a specific permission."""
        return (self.role_permissions & perm) == perm

    def add_permission(self, perm):
        """Add a permission to the role."""
        if not self.has_permission(perm):
            self.role_permissions += perm

    def remove_permission(self, perm):
        """Remove a permission from the role."""
        if self.has_permission(perm):
            self.role_permissions -= perm

    def reset_permissions(self):
        """Reset all permissions for the role."""
        self.role_permissions = 0

    @staticmethod
    def insert_roles():
        """Create or update roles with a predefined set of permissions."""
        roles = {
            "Staff": (
                Permission.LOGIN |
                Permission.MANAGE_HOUSES |
                Permission.MANAGE_TENANTS |
                Permission.MANAGE_PAYMENTS
            ),
            "Administrator": (0xff)  # All permissions
        }
        default_role = "Staff"

        for r_name, r_perms in roles.items():
            role = Role.query.filter_by(role_name=r_name).first()
            if role is None:
                role = Role(role_name=r_name)
                logger.info(f"Creating role: {r_name}")

            role.reset_permissions()
            role.add_permission(r_perms)
            role.role_default = (role.role_name == default_role)
            db.session.add(role)

        db.session.commit()
        logger.info("Roles initialized or updated successfully!")


class AgencieInfoModelMixin(db.Model):
    __abstract__ = True

    vn_agencie_name = db.Column(db.String(80), unique=True, nullable=True)
    vn_business_number = db.Column(db.String(80), unique=True, nullable=True)


class User(
    UserMixin, DefaultUserInfoModel, AgencieInfoModelMixin, TimestampMixin, db.Model
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
        "HouseOwner",
        backref="house_owner",
        lazy="dynamic",
        order_by="desc(HouseOwner.vn_created_at)",
    )
    houses = db.relationship(
        "House",
        lazy="dynamic",
        backref="user_houses",
        order_by="desc(House.vn_created_at)",
    )
    tenants = db.relationship(
        "Tenant",
        lazy="dynamic",
        backref="user_tenants",
        order_by="desc(Tenant.vn_created_at)",
    )
    payments = db.relationship(
        "Payment",
        lazy="dynamic",
        backref="user_payments",
        order_by="desc(Payment.vn_pay_date)",
    )
    transfers = db.relationship(
        "TransferRequest",
        lazy="dynamic",
        backref="user_transfer_requests",
        order_by="desc(TransferRequest.vn_created_at)",
    )
    percent = db.relationship("Percent", uselist=False, back_populates="user")

    @property
    def vn_devise(self):
        return self.vn_device or "XOF"

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def __str__(self):
        return self.vn_fullname or self.vn_agencie_name

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, fullname={self.vn_fullname!r})"

    def can(self, perm):
        """Check if the user has a required permission."""
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        """Check if the user is an administrator."""
        return self.can(Permission.ADMIN)

    def set_password(self, password):
        self.vn_password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.vn_password, password)

    def get_owner_percent(self) -> float:
        return getattr(self.percent, "vn_owner_percent", 7)

    def get_company_percent(self) -> float:
        return getattr(self.percent, "vn_company_percent", 6)

    @staticmethod
    def create_admin():
        addr_email = current_app.config["ADMIN_EMAIL"]

        if User.query.filter_by(vn_addr_email=addr_email).first():
            logger.info(f"Admin user with email {addr_email} already exists.")
            return

        try:
            user = User(
                vn_addr_email=addr_email,
                vn_fullname=current_app.config["ADMIN_USERNAME"],
                vn_phonenumber_one=current_app.config["ADMIN_PHONE_NUMBER"]
            )
            user.set_password(current_app.config["ADMIN_PASSWORD"])

            admin_role = Role.query.filter_by(role_name="Administrator").first()
            if admin_role:
                user.role = admin_role
            else:
                logger.warning("Administrator role not found. Admin user will have no role.")

            db.session.add(user)
            db.session.commit()
            logger.info(f"Admin user {addr_email} created successfully.")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create admin user: {e}")


class Percent(TimestampMixin):
    __tablename__ = "percent"

    vn_user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    user = db.relationship("User", back_populates="percent")
    vn_owner_percent = db.Column(db.Float, default=7, nullable=True)
    vn_company_percent = db.Column(db.Float, default=6, nullable=True)

    def __init__(self, user, vn_owner_percent=7, vn_company_percent=6):
        self.user = user
        self.vn_owner_percent = vn_owner_percent
        self.vn_company_percent = vn_company_percent

    def __str__(self):
        return self.user

    def __repr__(self):
        return f"Percent({self.id}, {self.owner_percent}, {self.company_percent})"


# --- Tenant Models ---


class HouseOwner(DefaultUserInfoModel, TimestampMixin):
    __tablename__ = "houseowner"

    vn_owner_id = db.Column(
        db.String(5), nullable=True, unique=True, default=id_generator
    )
    vn_avatar = db.Column(db.String(80), nullable=True)
    vn_user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="cascade"))
    vn_owner_percent = db.Column(db.Float, default=0, nullable=True)

    @property
    def number_houses(self):
        return len(self.owner_houses)

    @property
    def number_tenants(self):
        return len(self.owner_tenants)

    @property
    def total_amount(self):
        return sum(h.vn_house_rent for h in self.owner_houses if h.vn_house_is_open)

    @property
    def amount_repaid(self):
        # Using a logical assumption or matching existing pattern
        # This can be refined but for now we'll sum the 90% of open house rents 
        # or just the total rent for now.
        return sum(h.vn_house_rent for h in self.owner_houses if h.vn_house_is_open)

    def __str__(self):
        return f"{self.vn_fullname} - {self.vn_phonenumber_one}"

    def __repr__(self):
        return f"HouseOwner({self.id}, {self.vn_fullname})"

    def get_owner_id(self):
        return f"#{self.vn_owner_id}"


class House(TimestampMixin):
    __tablename__ = "house"

    vn_house_id = db.Column(
        db.String(5), nullable=False, unique=True, default=id_generator
    )
    vn_house_type = db.Column(db.String(80), nullable=False)
    vn_house_rent = db.Column(db.Float, nullable=False)
    vn_house_guaranty = db.Column(db.Float, nullable=False)
    vn_house_month = db.Column(db.Integer, nullable=False, default=1)
    vn_house_number_room = db.Column(db.Integer, nullable=False, default=1)
    vn_house_address = db.Column(db.String(120), nullable=False)
    vn_house_is_open = db.Column(db.Boolean, nullable=False, default=False)

    vn_house_lease_start_date = db.Column(
        db.Date, nullable=True, default=datetime.utcnow()
    )
    vn_house_lease_end_date = db.Column(
        db.Date, nullable=True, default=datetime.utcnow()
    )

    vn_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    vn_owner_id = db.Column(db.Integer, db.ForeignKey("houseowner.id"))
    owner = db.relationship(
        "HouseOwner",
        backref="owner_houses",
        order_by="desc(House.vn_created_at)",
    )

    def house_disable(self):
        """Set house as available (not occupied)."""
        self.vn_house_is_open = False
        db.session.add(self)
        db.session.commit()

    def house_occupy(self):
        """Set house as occupied."""
        self.vn_house_is_open = True
        db.session.add(self)
        db.session.commit()

    def __str__(self) -> str:
        return f"{self.vn_house_id} - {self.vn_house_type} - {self.vn_house_rent}"

    def __repr__(self) -> str:
        return f"House({self.id}, {self.vn_house_type})"

    def get_house_id(self) -> str:
        return f"#{self.vn_house_id}"


class Tenant(DefaultUserInfoModel, TimestampMixin):
    __tablename__ = "tenant"

    vn_tenant_id = db.Column(
        db.String(5),
        nullable=False,
        unique=True,
        default=id_generator,
    )
    vn_birthdate = db.Column(db.Date, nullable=True)

    vn_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    vn_house_id = db.Column(db.Integer, db.ForeignKey("house.id"))
    house = db.relationship(
        "House",
        uselist=False,
        backref="house_tenants",
        order_by="desc(Tenant.vn_created_at)",
    )

    vn_owner_id = db.Column(db.Integer, db.ForeignKey("houseowner.id"))
    owner = db.relationship(
        "HouseOwner",
        backref="owner_tenants",
        order_by="desc(Tenant.vn_created_at)",
    )

    def __str__(self):
        return f"{self.id} {self.vn_fullname}"

    def __repr__(self) -> str:
        return f"Tenant({self.id}, {self.vn_tenant_id})"

    def get_tenant_id(self) -> str:
        return f"#{self.vn_tenant_id}"

    @classmethod
    def get_tenants_list(cls):
        return cls.query.filter_by(vn_user_id=current_user.id).order_by(db.desc("vn_created_at"))


# --- Payment Models ---


class Payment(TimestampMixin):
    __tablename__ = "payment"

    vn_payment_id = db.Column(
        db.String(5), nullable=True, unique=True, default=id_generator
    )
    vn_transaction_id = db.Column(db.String(10), nullable=True, unique=True)
    vn_pay_amount = db.Column(db.Float, nullable=False)
    vn_pay_late_penalty = db.Column(db.Float, nullable=True)
    vn_pay_date = db.Column(db.Date, nullable=False)
    vn_pay_status = db.Column(db.Boolean, default=False)
    vn_cinetpay_data = db.Column(db.JSON, default=False)

    vn_payee_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    vn_owner_id = db.Column(db.Integer, db.ForeignKey("houseowner.id"))
    owner = db.relationship(
        "HouseOwner",
        backref="owner_payment",
        order_by="desc(Payment.vn_pay_date)",
    )

    vn_tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"))
    tenant = db.relationship(
        "Tenant",
        backref="tenant_payment",
        order_by="desc(Payment.vn_pay_date)",
    )

    vn_house_id = db.Column(db.Integer, db.ForeignKey("house.id"))
    house = db.relationship(
        "House", backref="house_payment", order_by="desc(Payment.vn_pay_date)"
    )

    def __str__(self):
        return self.vn_transaction_id

    def __repr__(self) -> str:
        return f"Payment(id={self.id!r}, fullname={self.vn_transaction_id!r}, {self.vn_pay_date})"

    @classmethod
    def find_by_transaction_id(cls, transaction_id):
        return cls.query.filter_by(vn_transaction_id=transaction_id).first()

    def get_status_payment(self):
        return "payé" if self.vn_pay_status else "impayé"


class TransferRequest(TimestampMixin):
    __tablename__ = "transfer_request"

    vn_transfer_id = db.Column(
        db.String(5), nullable=True, unique=True, default=id_generator
    )
    vn_user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    vn_trans_amount = db.Column(db.Float, nullable=False)
    vn_trans_status = db.Column(db.Boolean, default=False)
    vn_withdrawal_number = db.Column(db.String(50), nullable=True)
    vn_withdrawal_method = db.Column(db.String(50), nullable=True)
    vn_cinetpay_data = db.Column(db.JSON, default=False)

    def __str__(self):
        return self.vn_trans_amount

    def __repr__(self):
        return f"TransferRequest({self.vn_transfer_id}, {self.vn_trans_status})"

    def get_status_transfer(self) -> str:
        return "en cours" if self.vn_trans_status else "en cours"


# --- Flask-Login Configuration ---


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)
