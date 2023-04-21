from datetime import datetime

import jwt
from flask import current_app
from flask import request
from flask_login import AnonymousUserMixin
from flask_login import current_user
from flask_login import UserMixin
from src import db
from src import login_manager
from src.constants import COUNTRY_DEFAULT
from src.mixins.models import DefaultUserInfoModel
from src.mixins.models import TimestampMixin
from src.tenant.models import VNHouse
from src.tenant.models import VNHouseOwner
from src.tenant.models import VNTenant
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash


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
            "Administrateur": (0xFF, False),
        }
        default_role = "Administrateur"
        for r in roles:
            role = VNRole.query.filter_by(role_name=r).first()
            if role is None:
                role = VNRole(role_name=r)
            role.reset_permission()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = role.role_name == default_role
            db.session.add(role)
        db.session.commit()


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

    def __str__(self):
        return self.vn_fullname or self.vn_agencie_name

    def __repr__(self):
        return f"VNUser({self.id}, {self.vn_fullname})"

    def to_json(self):
        json_user = {
            "user_id": self.uuid,
            "fullname": self.vn_fullname,
            "addr_email": self.vn_addr_email,
            "profession": self.vn_profession,
            "parent_name": self.vn_parent_name,
            "phonenumber_one": self.vn_phonenumber_one,
            "phonenumber_two": self.vn_phonenumber_two,
            "cni_number": self.vn_cni_number,
            "location": self.vn_location,
            "country": self.vn_country,
            "agencie_name": self.vn_agencie_name,
            "business_number": self.vn_business_number,
            "devise": self.vn_device,
            "find_us": self.vn_find_us,
            "ip_address": self.vn_ip_address,
            "is_company": self.vn_company,
            "is_owner": self.vn_house_owner,
            "is_admin": self.is_administrator(),
            "is_activated": self.vn_activated,
            "last_seen": self.vn_last_seen,
            "created_at": self.vn_created_at.strftime("%d-%m-%Y"),
            "total_house_amount": self.total_houses_amount(),
            "total_house_percent": self.total_houses_percent(),
            "payments_list": self.get_payments_list(),
            "payments_count": self.get_payments_count(),
            "total_payment_month": self.total_payments_month(),
            "houses_count": self.get_houses_count(),
            "houses_close_count": self.get_houses_close_count(),
            "houses_open_count": self.get_houses_open_count(),
            "houses_list": self.get_houses_list(),
            "tenants_list": self.get_tenants_list(),
            "tenants_count": self.get_tenants_count(),
            "owners_list": self.get_houseowners_list(),
            "owners_count": self.get_houseowners_count(),
        }
        return json_user

    def set_password(self, password):
        self.vn_password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.vn_password, password)

    def get_payments_list(self):
        payments_list = self.payments.filter_by(vn_payee_id=current_user.id).all()
        return [p.to_json() for p in payments_list]

    def get_payments_count(self):
        payments_count = self.payments.filter_by(
            vn_payee_id=current_user.id, vn_pay_status=True
        ).count()
        return payments_count

    def get_houseowners_list(self):
        owners_list = self.houseowners.filter_by(vn_user_id=current_user.id).all()
        return [o.to_json() for o in owners_list]

    def get_houseowners_count(self):
        houseowners_count = self.houseowners.filter_by(
            vn_user_id=current_user.id
        ).count()
        return houseowners_count

    def get_houses_list(self):
        houses_list = self.houses.filter_by(vn_user_id=current_user.id).all()
        return [h.to_json() for h in houses_list]

    def get_houses_count(self):
        houses_count = self.houses.filter_by(vn_user_id=current_user.id).count()
        return houses_count

    def get_houses_close_count(self):
        houses_close_count = self.houses.filter_by(
            vn_house_is_open=True, vn_user_id=current_user.id
        ).count()
        return houses_close_count

    def get_houses_open_count(self):
        houses_open_count = self.houses.filter_by(
            vn_house_is_open=False, vn_user_id=current_user.id
        ).count()
        return houses_open_count

    def get_tenants_list(self):
        tenants_list = self.tenants.filter_by(vn_user_id=current_user.id).all()
        return [t.to_json() for t in tenants_list]

    def get_tenants_count(self):
        tenants_count = self.tenants.filter_by(vn_user_id=current_user.id).count()
        return tenants_count

    @staticmethod
    def verify_reset_password_token(token):
        try:
            user_id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["reset_password"]
        except Exception as e:
            print(e)
            return
        return db.session(VNUser).query.get(int(user_id))

    def generate_reset_token(self, expires_in=3600):
        secret_key = current_app.config["SECRET_KEY"]
        return jwt.encode(
            {"auth_view.reset_password": self.id, "exp": expires_in},
            secret_key,
            algorithm="HS256",
        )

    def generate_email_change_token(self, new_email, expiration=3600):
        secret_key = current_app.config["SECRET_KEY"]
        return jwt.decode(
            {"auth_view.change_email": self.id, "new_email": new_email},
            secret_key,
            algorithm=["HS256"],
        )

    def change_email(self, token):
        secret_key = current_app.config["SECRET_KEY"]
        try:
            data = jwt.decode(token, secret_key, algorithm="HS256")
        except Exception as e:
            print(e)
            return False

        if data.get("change_email") != self.id:
            return False
        new_email = data.get("new_email")

        if new_email is None:
            return False

        if self.query.filter_by(vn_addr_email=new_email).first() is not None:
            return False

        self.email = new_email
        db.session.add(self)

        return True

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

    @staticmethod
    def get_users_list():
        users = VNUser.query.filter_by(vn_activated=True)
        return users

    @staticmethod
    def get_user_logged():
        user = VNUser.query.filter_by(id=current_user.id, vn_activated=True).first()
        return user

    def total_houses_amount(self):
        user_houses = self.houses.filter_by(
            vn_house_is_open=True, vn_user_id=current_user.id
        ).all()
        total = sum(house.vn_house_rent for house in user_houses)
        return "{:,.2f}".format(total)

    def total_houses_percent(self):
        user_houses = (
            self.houses.filter_by(vn_house_is_open=True, vn_user_id=current_user.id)
            .join(VNHouseOwner)
            .filter(VNHouseOwner.vn_user_id.isnot(None))
            .all()
        )
        total_percent = sum(
            house.get_house_rent_with_percent() for house in user_houses
        )
        return "{:,.2f}".format(total_percent)

    def total_payments_month(self):

        from src.payment import VNPayment
        from src.tenant import VNHouse, VNHouseOwner, VNTenant

        now = datetime.now()
        month = now.month
        year = now.year

        total_payments = (
            db.session.query(db.func.sum(VNPayment.vn_pay_amount))
            .join(VNHouse)
            .join(VNTenant)
            .join(VNHouseOwner)
            .join(VNUser)
            .filter(
                VNUser.uuid == current_user.uuid,
                VNPayment.vn_pay_status,
                db.extract("month", VNPayment.vn_pay_date) == month,
                db.extract("year", VNPayment.vn_pay_date) == year,
            )
            .scalar()
        )
        total_payment_month = total_payments or 0
        return "{:,.2f}".format(total_payment_month)

    @staticmethod
    def get_label(user):
        return user.get_name()

    def get_name(self):
        if self.vn_house_owner:
            return self.vn_fullname
        if self.vn_company:
            return self.vn_agencie_name

    @staticmethod
    def get_ownerbymonth():
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
    def get_tenantbymonth():
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
    def count_available_properties():
        current_user_id = current_user.id

        available_properties = (
            db.session.query(
                db.func.sum(
                    db.cast(
                        VNHouse.vn_house_is_open & (VNUser.id == current_user_id),
                        db.Integer,
                    )
                ),
                db.func.sum(
                    db.cast(
                        ~VNHouse.vn_house_is_open & (VNUser.id == current_user_id),
                        db.Integer,
                    )
                ),
            )
            .join(VNUser)
            .all()
        )

        return available_properties

    @staticmethod
    def create_admin():

        """
        Create the admin user.
        """
        import logging

        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger(__name__)

        addr_email = current_app.config["ADMIN_EMAIL"]
        fullname = current_app.config["ADMIN_USERNAME"]
        password = current_app.config["ADMIN_PASSWORD"]
        phonenumber_one = current_app.config["ADMIN_PHONE_NUMBER"]

        try:
            user = VNUser(vn_addr_email=addr_email)
            user.vn_fullname = fullname
            user.vn_password = generate_password_hash(password)
            user.vn_phonenumber_one = phonenumber_one
            user.vn_role_id = Permission.ADMIN
            db.session.add(user)
            db.session.commit()
            logger.info(f"Admin with email {addr_email} created successfully!")
        except Exception as e:
            logger.warning(f"Couldn't create admin user, because {e}")


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(VNUser).get(user_id)
