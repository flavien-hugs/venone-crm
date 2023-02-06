import random
import string

from flask_login import current_user
from src import db
from src.mixins.models import DefaultUserInfoModel
from src.mixins.models import TimestampMixin


def id_generator():
    return "".join(random.choices(string.digits, k=5))


class VNHouseOwner(DefaultUserInfoModel, TimestampMixin):

    __tablename__ = "houseowner"

    vn_owner_id = db.Column(
        db.String(5), name="owner ID", nullable=True, unique=True, default=id_generator
    )
    vn_avatar = db.Column(db.String(80), name="owner avatar", nullable=True)
    vn_user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=False
    )
    houses = db.relationship(
        "VNHouse",
        cascade="all,delete",
        backref="house",
        passive_deletes=True,
        lazy=True,
    )

    def __str__(self):
        return self.vn_fullname

    def __repr__(self):
        return "<VNHouseOwner %r>" % self.vn_fullname, self.vn_phonenumber_one

    @staticmethod
    def houseowner_list_query():
        return VNHouseOwner.query.filter_by(
            vn_user_id=current_user.id, vn_activated=True
        )

    @staticmethod
    def get_houseowner_name(houseowner):
        return houseowner.vn_fullname

    @staticmethod
    def get_houseowner(owner_uuid):
        return VNHouseOwner.query.filter_by(uuid=owner_uuid).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def desactivate(self):
        self.vn_activated = False
        db.session.commit()

    def remove(self):
        db.session.delete(self)
        db.session.commit()


class VNHouse(TimestampMixin):

    __tablename__ = "house"

    vn_house_id = db.Column(
        db.String(5), name="house ID", nullable=False, unique=True, default=id_generator
    )
    vn_house_type = db.Column(db.String(20), name="house type", nullable=False)
    vn_house_rent = db.Column(
        db.Integer, name="rent/month", nullable=False, default=10000
    )
    vn_house_guaranty = db.Column(
        db.Integer, name="security deposit", nullable=False, default=10000
    )
    vn_house_month = db.Column(
        db.Integer, name="number of months", nullable=False, default=3
    )
    vn_house_address = db.Column(db.String(120), name="house address", nullable=False)
    vn_house_is_open = db.Column(
        db.Integer, name="house is open", nullable=False, default=3
    )
    vn_houseowner_id = db.Column(
        db.Integer, db.ForeignKey("houseowner.id", ondelete="SET NULL"), nullable=False
    )
    vn_activated = db.Column(db.Boolean, name="status", nullable=False, default=True)
    tenants = db.relationship(
        "VNTenant",
        cascade="all,delete",
        backref="tenant",
        passive_deletes=True,
        lazy=True,
    )

    def __str__(self):
        return self.vn_fullname

    def __repr__(self):
        return "<VNHouse %r>" % self.vn_fullname, self.vn_phonenumber_one

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_house_id(house):
        return house.vn_house_id

    @staticmethod
    def get_house(house_id):
        return VNHouse.query.filter_by(uuid=house_id, vn_house_is_open=True).first()


class VNTenant(DefaultUserInfoModel, TimestampMixin):

    __tablename__ = "tenant"

    vn_tenant_id = db.Column(
        db.String(5),
        name="tenant ID",
        nullable=False,
        unique=True,
        default=id_generator,
    )
    vn_avatar = db.Column(db.String(80), name="tenant avatar", nullable=True)
    vn_birthdate = db.Column(db.Date, name="tenant birth date", nullable=True)
    vn_house_id = db.Column(
        db.Integer, db.ForeignKey("house.id", ondelete="SET NULL"), nullable=False
    )
    vn_user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=False
    )

    def __str__(self):
        return self.vn_fullname

    def __repr__(self):
        return "<VNTenant %r>" % self.vn_fullname, self.vn_phonenumber_one

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def tenant_list_query():
        return VNTenant.query.where(VNTenant.vn_user_id == current_user.id).filter_by(
            vn_activated=True
        )

    @staticmethod
    def get_tenant_name(tenant):
        return tenant.vn_fullname

    @staticmethod
    def get_tenant(tenant_id):
        return VNTenant.query.filter_by(
            uuid=tenant_id, vn_user_id=current_user.id
        ).first()
