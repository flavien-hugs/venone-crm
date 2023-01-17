from datetime import date, datetime

from flask import request

from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy_utils import UUIDType, EmailType, PhoneNumberType, IPAddressType

from .. import db
from slugify import slugify
from .constants import Gender, Country, AccountType
from src.mixins.models import TimestampMixin


class Permission:
    ADMIN = 0x05
    STAFF = 0x07


class VNRole(db.Model):

    __tablename__ = "roles"

    id = db.Column(db.Integer, index=True, primary_key=True)
    role_permissions = db.Column(db.Integer)
    role_name = db.Column(db.String(64), unique=True)
    role_default = db.Column(db.Boolean, default=False, index=True)
    users = db.relationship("VNUser", backref="role", lazy="dynamic")

    def __init__(self, **kwagrs):
        super(VNRole, self).__init__(**kwagrs)
        if self.role_permissions is None:
            self.role_permissions = 0

    def __repr__(self):
        return f'<User {self.role_name!r}>'

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
            "Administrateur": (0xff, False),
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

    vn_agencie_name = db.Column(db.String(80), unique=True, nullable=False)
    vn_business_number = db.Column(db.String(80), unique=True, nullable=False)


"""
class VNUser:
    id: int primary key
    vn_user_gender: str
    vn_user_fullname: str
    vn_user_addr_email: str
    vn_user_cni_number: str
    vn_user_profession: str
    vn_user_parent_name: str
    vn_user_phonenumber_one: str
    vn_user_phonenumber_two: str
    vn_user_avatar: str
    vn_agencie_name: str
    vn_business_number: str
    vn_user_account_type: str
    vn_user_password: str
    vn_user_activated: bool
    vn_user_birthdate: date
    vn_user_last_seen: date
    vn_ip_address: str
"""


class VNUser(VNAgencieInfoModelMixin, TimestampMixin, db.Model):

    __tablename__ = "user"

    vn_user_gender = db.Column(
        db.Enum(Gender), nullable=False, default=Gender.HOMME)
    vn_user_fullname = db.Column(db.String(80), nullable=False)
    vn_user_addr_email = db.Column(db.String(120), unique=True, nullable=False)
    vn_user_profession = db.Column(db.String(180), nullable=True)
    vn_user_parent_name = db.Column(db.String(180), nullable=True)
    vn_user_phonenumber_one = db.Column(
        PhoneNumberType(), unique=True, nullable=False)
    vn_user_phonenumber_two = db.Column(
        PhoneNumberType(), unique=True, nullable=True)
    vn_user_cni_number = db.Column(db.String(11), unique=True, nullable=True)
    vn_user_location = db.Column(db.String(180), nullable=True)
    vn_user_country = db.Column(
        db.Enum(Country), nullable=False, default=Country.CIV)
    vn_user_avatar = db.Column(db.String(32), nullable=True)
    vn_user_account_type = db.Column(
        db.Enum(AccountType),
        default=AccountType.IS_HOUSE_OWNER
    )
    vn_user_activated = db.Column(db.Boolean, default=False)
    vn_user_password = db.Column(db.String(80), nullable=False)
    vn_user_birthdate = db.Column(db.Date, default=date.today())
    vn_user_last_seen = db.Column(db.DateTime, onupdate=datetime.utcnow())
    vn_ip_address = db.Column(IPAddressType)
    vn_role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)

    def __repr__(self):
        return '<VNUser %r>' % self.vn_user_fullname

    def can(self, permissions):
        return (
            self.role is not None and
            (self.role.vn_role_permissions & vn_role_permissions) == permissions
        )

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, user_fullname, user_addr_email):
        self.user_fullname = user_fullname
        self.user_addr_email = user_addr_email
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.vn_user_last_seen = datetime.utcnow()
        db.session.add(self)
