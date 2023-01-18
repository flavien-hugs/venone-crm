from time import time
from datetime import date, datetime

from flask import current_app, request

from sqlalchemy_utils import EmailType, PhoneNumberType, ChoiceType
from werkzeug.security import generate_password_hash, check_password_hash

from .. import db, login_manager
from ..mixins.models import TimestampMixin
from .constants import Gender, Country, AccountType
from flask_login import UserMixin, AnonymousUserMixin

class Permission:
    ADMIN = 5
    STAFF = 7


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

    vn_agencie_name = db.Column(db.String(80), unique=True, nullable=True)
    vn_business_number = db.Column(db.String(80), unique=True, nullable=True)


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


class VNUser(UserMixin, VNAgencieInfoModelMixin, TimestampMixin, db.Model):

    __tablename__ = "user"

    vn_user_gender = db.Column(ChoiceType(Gender), default=Gender.HOMME)
    vn_user_fullname = db.Column(db.String(80), nullable=False)
    vn_user_addr_email = db.Column(EmailType(), unique=True, nullable=False)
    vn_user_profession = db.Column(db.String(100), nullable=True)
    vn_user_parent_name = db.Column(db.String(80), nullable=True)
    vn_user_phonenumber_one = db.Column(
        PhoneNumberType(), unique=True, nullable=True)
    vn_user_phonenumber_two = db.Column(
        PhoneNumberType(), unique=True, nullable=True)
    vn_user_cni_number = db.Column(db.String(11), unique=True, nullable=True)
    vn_user_location = db.Column(db.String(180), nullable=True)
    vn_user_country = db.Column(ChoiceType(Country), default=Country.CIV)
    vn_user_avatar = db.Column(db.String(32), nullable=True)
    vn_user_account_type = db.Column(
        ChoiceType(AccountType),
        default=AccountType.IS_HOUSE_OWNER
    )
    vn_user_activated = db.Column(db.Boolean, default=False)
    vn_user_password = db.Column(db.String(180), nullable=False)
    vn_user_birthdate = db.Column(db.Date, nullable=True)
    vn_user_last_seen = db.Column(db.DateTime, onupdate=datetime.utcnow())
    vn_role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=True)

    def __repr__(self):
        return '<VNUser %r>' % self.vn_user_fullname

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.vn_user_password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.vn_user_password, password)

    def reset_password_token(self, expires_in=3600):
        return jwt.encode(
            {"auth.reset_password_page": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_reset_password_token(token):
        key_current_app_config = current_app.config["SECRET_KEY"]
        id = jwt.decode(token, key_current_app_config, algorithms=["HS256"])[
            "auth.reset_passwordage"
        ]
        return User.query.get(id)

    def can(self, perm):
        return (
            self.role is not None
            and self.role.has_permission(perm)
        )

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, vn_user_fullname):
        self.vn_user_fullname = vn_user_fullname
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def ping(self):
        self.vn_user_last_seen = datetime.utcnow()
        db.session.add(self)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return VNUser.query.get(int(user_id))
