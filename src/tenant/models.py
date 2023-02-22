import random
import string

from flask import url_for, current_app
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
    vn_avatar = db.Column(db.String(80), nullable=True)
    vn_user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )
    houses = db.relationship(
        "VNHouse",
        backref="owner_house",
        passive_deletes=True,
        single_parent=True,
        lazy="dynamic",
        cascade="all, delete, delete-orphan",
        order_by="desc(VNHouse.vn_created_at)"
    )
    tenants = db.relationship(
        "VNTenant",
        backref="owner_tenant",
        passive_deletes=True,
        single_parent=True,
        lazy="dynamic",
        cascade="all, delete, delete-orphan",
        order_by="desc(VNTenant.vn_created_at)"
    )

    def to_json(self):
        json_houseowner = {
            "user_uuid": current_user.uuid,
            "owner_uuid": self.uuid,
            "owner_id": self.get_owner_id(),
            "gender": self.vn_gender,
            "fullname": self.vn_fullname,
            "addr_email": self.vn_addr_email,
            "profession": self.vn_profession,
            "parent_name": self.vn_parent_name,
            "card_number": self.vn_cni_number,
            "location": self.vn_location,
            "phonenumber_one": self.vn_phonenumber_one,
            "phonenumber_two": self.vn_phonenumber_two,
            "number_houses": self.houses.count(),
            "activated": self.get_owner_available(),
            "houses": [house.to_json() for house in self.houses],
            "number_tenants": self.tenants.count(),
            "tenants": [tenant.to_json() for tenant in self.tenants],
            "owner_url": url_for(
                "api.get_houseowner",
                owner_uuid=self.uuid, _external=True
            ),
            "owner_delete_url": url_for(
                "api.delete_houseowner", owner_uuid=self.uuid, _external=True
            ),
            "houses_url": url_for(
                "api.get_houseowner_houses", owner_uuid=self.uuid, _external=True
            ),
            "tenants_url": url_for(
                "api.get_houseowner_tenants", owner_uuid=self.uuid, _external=True
            ),
            "created_at": self.vn_created_at.strftime('%d %B %Y'),
        }
        return json_houseowner

    def __str__(self):
        return self.vn_fullname

    def __repr__(self):
        return f"VNHouseOwner({self.id}, {self.vn_fullname})"

    def get_owner_id(self):
        return f"#{self.vn_owner_id}"

    @staticmethod
    def get_houseowner_name(houseowner):
        return houseowner.vn_fullname

    def get_owner_available(self):
        if self.vn_activated:
            return "Compte actif"
        return "Compte inactif"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def disable(self):
        self.vn_activated = False
        db.session.commit()

    def remove(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_houseowners_list():
        return VNHouseOwner.query.filter_by(vn_user_id=current_user.id, vn_activated=True)

    @staticmethod
    def get_houseowner(owner_uuid):
        return VNHouseOwner.query.filter_by(vn_user_id=current_user.id, uuid=owner_uuid).first()

    @staticmethod
    def get_owner_tenant(owner_uuid):
        return VNTenant.query.filter_by(uuid=owner_uuid, vn_houseowner_id=self.id, vn_user_id=current_user.uuid).first()


class VNHouse(TimestampMixin):

    __tablename__ = "house"

    vn_house_id = db.Column(
        db.String(5), nullable=False, unique=True, default=id_generator
    )
    vn_house_type = db.Column(db.String(20), nullable=False)
    vn_house_rent = db.Column(
        db.Integer, nullable=False, default=10000
    )
    vn_house_guaranty = db.Column(
        db.Integer, nullable=False, default=10000
    )
    vn_house_month = db.Column(
        db.Integer, nullable=False, default=1
    )
    vn_number_or_room = db.Column(
        db.Integer, nullable=False, default=1
    )
    vn_house_address = db.Column(db.String(120), nullable=False)
    vn_house_is_open = db.Column(
        db.Boolean, nullable=False, default=True
    )
    vn_houseowner_id = db.Column(
        db.Integer, db.ForeignKey("houseowner.id"), nullable=True
    )
    vn_activated = db.Column(db.Boolean, nullable=False, default=True)
    vn_user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )
    tenants = db.relationship(
        "VNTenant",
        backref="house",
        passive_deletes=True,
        single_parent=True,
        lazy="dynamic",
        cascade="all, delete, delete-orphan",
        order_by="desc(VNTenant.vn_created_at)"
    )

    def to_json(self):
        json_house = {
            "user_uuid": current_user.uuid,
            "house_uuid": self.uuid,
            "house_id": self.get_house_id(),
            "house_type": self.vn_house_type,
            "house_rent": self.vn_house_rent,
            "house_guaranty": self.vn_house_guaranty,
            "house_month": self.vn_house_month,
            "number_or_room": self.vn_number_or_room,
            "house_address": self.vn_house_address,
            "houseowner_fullname": self.owner_house.vn_fullname,
            "tenants": [tenant.to_json() for tenant in self.tenants],
            "house_url": url_for("api.get_house", uuid=self.uuid, _external=True),
            "owner_url": url_for(
                "api.get_houseowner", owner_uuid=self.uuid, _external=True
            ),
            "tenant_url": url_for(
                "api.get_house_tenant", uuid=self.uuid, _external=True
            ),
            "house_is_open": self.vn_house_is_open,
            "house_status": self.get_house_open(),
            "created_at": self.vn_created_at.strftime('%d %B %Y'),
        }
        return json_house

    def __str__(self):
        return self.vn_house_type

    def __repr__(self):
        return f"VNHouse({self.id}, {self.vn_house_type})"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def disable(self):
        self.vn_activated = False
        self.vn_house_is_open = False
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_house_open(self):
        if self.vn_house_is_open:
            return "Indisponible"
        return "Disponible"

    def get_house_id(self):
        return f"#{self.vn_house_id}"

    @staticmethod
    def get_houses_list():
        return VNHouse.query.filter_by(vn_user_id=current_user.id)

    @staticmethod
    def get_house(house_uuid):
        return VNHouse.query.filter_by(uuid=house_uuid, vn_user_id=current_user.id).first()


class VNTenant(DefaultUserInfoModel, TimestampMixin):

    __tablename__ = "tenant"

    vn_tenant_id = db.Column(
        db.String(5),
        nullable=False,
        unique=True,
        default=id_generator,
    )
    vn_birthdate = db.Column(db.Date, nullable=True)
    vn_house_id = db.Column(
        db.Integer, db.ForeignKey("house.id"), nullable=True
    )
    vn_houseowner_id = db.Column(
        db.Integer,
        db.ForeignKey("houseowner.id"),
        nullable=True,
    )
    vn_user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
    )

    def to_json(self):
        json_tenant = {
            "user_uuid": current_user.uuid,
            "tenant_uuid": self.uuid,
            "tenant_id": self.get_tenant_id(),
            "gender": self.vn_gender,
            "fullname": self.vn_fullname,
            "addr_email": self.vn_addr_email,
            "profession": self.vn_profession,
            "parent_name": self.vn_parent_name,
            "card_number": self.vn_cni_number,
            "location": self.vn_location,
            "phonenumber_one": self.vn_phonenumber_one,
            "phonenumber_two": self.vn_phonenumber_two,
            "house_type": f"{self.house.vn_house_type} de {self.house.vn_house_rent}",
            "activated": self.vn_activated,
            "houseowner_fullname": self.owner_tenant.vn_fullname,
            "tenant_url": url_for("api.get_tenant", uuid=self.uuid, _external=True),
            "owner_url": url_for(
                "api.get_houseowner", owner_uuid=self.owner_tenant.uuid, _external=True
            ),
            "house_url": url_for(
                "api.get_house", uuid=self.house.uuid, _external=True
            ),
            "created_at": self.vn_created_at.strftime('%d %B %Y'),
        }
        return json_tenant

    def __str__(self):
        return self.vn_fullname

    def __repr__(self):
        return f"VNTenant({self.id}, {self.vn_tenant_id})"

    def get_tenant_id(self):
        return f"#{self.vn_tenant_id}"

    def disable(self):
        self.vn_activated = False
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_tenant_name(tenant):
        return tenant.vn_fullname

    @staticmethod
    def get_tenants_list():
        return VNTenant.query.filter_by(vn_user_id=current_user.id, vn_activated=True)

    @staticmethod
    def get_tenant(tenant_uuid):
        return VNTenant.query.filter_by(uuid=tenant_uuid, vn_user_id=current_user.id).first()
