from datetime import datetime

import jwt
from flask import current_app
from flask import request
from flask import url_for
from flask_login import AnonymousUserMixin
from flask_login import current_user
from flask_login import UserMixin
from src import db
from src import login_manager
from src.mixins.models import DefaultUserInfoModel
from src.mixins.models import TimestampMixin
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

    vn_country = db.Column(db.String(80), nullable=False)
    vn_avatar = db.Column(
        db.String(80), nullable=True, default="/static/img/element/avatar.png"
    )
    vn_activated = db.Column(db.Boolean, nullable=False, default=False)
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
        backref="houses",
        lazy="dynamic",
        order_by="desc(VNHouse.vn_created_at)",
    )
    tenants = db.relationship(
        "VNTenant",
        backref="tenants",
        lazy="dynamic",
        order_by="desc(VNTenant.vn_created_at)",
    )
    payments = db.relationship(
        "VNPayment",
        backref="payments",
        lazy="dynamic",
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
            "is_activated": self.vn_activated,
            "owner_count": self.houseowners.count(),
            "house_count": self.houses.count(),
            "tenant_count": self.tenants.count(),
            "payment": self.payments.count(),
            "last_seen": self.vn_last_seen,
            "created_at": self.vn_created_at.strftime("%d-%m-%Y"),
            "url": url_for("api.get_user", user_uuid=self.uuid, _external=True),
            "owners": url_for(
                "api.get_user_owners", user_uuid=self.uuid, _external=True
            ),
            "houses": url_for(
                "api.get_user_houses", user_uuid=self.uuid, _external=True
            ),
            "tenants": url_for(
                "api.get_user_tenants", user_uuid=self.uuid, _external=True
            ),
            "payments": url_for(
                "api.get_user_payments", user_uuid=self.uuid, _external=True
            ),
        }
        return json_user

    def set_password(self, password):
        self.vn_password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.vn_password, password)

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
    def get_current_user():
        return VNUser.query.filter_by(id=current_user.id).first()

    @staticmethod
    def get_label(user):
        return user.get_name()

    def get_name(self):
        if self.vn_house_owner:
            return self.vn_fullname
        if self.vn_company:
            return self.vn_agencie_name

    @staticmethod
    def get_users_list():
        return VNUser.query.filter_by(id=current_user.id, vn_activated=True)

    @staticmethod
    def get_user(user_uuid):
        return VNUser.query.filter_by(id=current_user.id, uuid=user_uuid).first()


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(VNUser).get(user_id)
