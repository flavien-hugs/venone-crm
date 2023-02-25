import random
import string
from datetime import date
from datetime import datetime
from datetime import timedelta

from flask import url_for
from flask_login import current_user
from src import db
from src.mixins.models import DefaultUserInfoModel
from src.mixins.models import TimestampMixin


def id_generator():
    return "".join(random.choices(string.digits, k=5))


class VNHouseOwner(DefaultUserInfoModel, TimestampMixin):

    """
    les propriétaires des maisons
    Ce modèle représentera les propriétaires des biens locatifs.
    """

    __tablename__ = "houseowner"

    vn_owner_id = db.Column(
        db.String(5), nullable=True, unique=True, default=id_generator
    )
    vn_avatar = db.Column(db.String(80), nullable=True)
    vn_user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="cascade"))

    houses = db.relationship(
        "VNHouse",
        lazy="dynamic",
        backref="owner_houses",
        single_parent=True,
        passive_deletes=True,
        cascade="all,delete,delete-orphan",
        order_by="desc(VNHouse.vn_created_at)",
    )

    tenants = db.relationship(
        "VNTenant",
        lazy="dynamic",
        backref="owner_tenants",
        single_parent=True,
        passive_deletes=True,
        cascade="all,delete,delete-orphan",
        order_by="desc(VNTenant.vn_created_at)",
    )

    payments = db.relationship(
        "VNPayment",
        backref="owner_payment",
        lazy="dynamic",
        order_by="desc(VNPayment.vn_pay_date)",
    )

    def to_json(self):
        json_owner = {
            "owner_uuid": self.uuid,
            "user_uuid": current_user.uuid,
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
            "activated": self.get_owner_available(),
            "houses": [h.to_json() for h in self.houses],
            "tenants": [t.to_json() for t in self.tenants],
            "payments": [p.to_json() for p in self.payments],
            "number_houses": self.houses.count(),
            "number_tenants": self.tenants.count(),
            "number_payments": self.payments.count(),
            "created_at": self.vn_created_at.strftime("%d-%m-%Y"),
            "_links": {
                "self": url_for("api.get_houseowner", owner_uuid=self.uuid),
                "houses_url": url_for(
                    "api.get_houseowner_houses", owner_uuid=self.uuid
                ),
                "tenants_url": url_for(
                    "api.get_houseowner_tenants", owner_uuid=self.uuid
                ),
            },
        }
        return json_owner

    @staticmethod
    def from_json(json_owner):
        fullname = json_owner.get("fullname")
        addr_email = json_owner.get("addr_email")
        profession = json_owner.get("addr_email")
        parent_name = json_owner.get("parent_name")
        card_number = json_owner.get("card_number")
        location = json_owner.get("location")
        phonenumber_one = json_owner.get("phonenumber_one")
        phonenumber_two = json_owner.get("phonenumber_two")

        return VNHouseOwner(
            fullname=fullname,
            addr_email=addr_email,
            profession=profession,
            parent_name=parent_name,
            card_number=card_number,
            location=location,
            phonenumber_one=phonenumber_one,
            phonenumber_two=phonenumber_two,
        )

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

    @staticmethod
    def get_owners_list():
        return VNHouseOwner.query.filter_by(
            vn_user_id=current_user.id, vn_activated=True
        )

    @staticmethod
    def get_owner(owner_uuid):
        return VNHouseOwner.query.filter_by(
            vn_user_id=current_user.id, uuid=owner_uuid
        ).first()

    @staticmethod
    def get_houses_list():
        return VNHouse.query.filter_by(vn_user_id=current_user.id, vn_activated=True)

    @staticmethod
    def get_house(owner_uuid):
        return VNHouse.query.filter_by(
            vn_user_id=current_user.id,
            uuid=owner_uuid,
        ).first()

    @staticmethod
    def get_tenants(owner_uuid):
        return VNTenant.query.filter_by(
            uuid=owner_uuid.uuid, vn_user_id=current_user.uuid
        ).first()

    @staticmethod
    def get_tenant(owner_uuid):
        return VNTenant.query.filter_by(
            uuid=owner_uuid.uuid, vn_user_id=current_user.uuid
        ).first()


class VNHouse(TimestampMixin):

    """
    VNHouse
    Ce modèle représentera les propriétés locatives et leurs propriétaires associés.
    """

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
    vn_house_is_open = db.Column(db.Boolean, nullable=False, default=True)

    vn_activated = db.Column(db.Boolean, nullable=False, default=True)

    vn_house_lease_start_date = db.Column(db.Date, nullable=False)
    vn_house_lease_end_date = db.Column(db.Date, nullable=False)

    vn_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    vn_owner_id = db.Column(db.Integer, db.ForeignKey("houseowner.id"))

    tenants = db.relationship(
        "VNTenant",
        backref="house_tenant",
        order_by="desc(VNTenant.vn_created_at)",
    )
    payments = db.relationship(
        "VNPayment", backref="house_payment", order_by="desc(VNPayment.vn_pay_date)"
    )

    def to_json(self):
        json_house = {
            "house_uuid": self.uuid,
            "user_uuid": current_user.uuid,
            "house_id": self.get_house_id(),
            "house_type": self.vn_house_type,
            "house_rent": self.vn_house_rent,
            "house_guaranty": self.vn_house_guaranty,
            "house_month": self.vn_house_month,
            "house_number_room": self.vn_house_number_room,
            "house_address": self.vn_house_address,
            "house_is_open": self.vn_house_is_open,
            "house_status": self.get_house_open(),
            "house_lease_start_date": self.vn_house_lease_start_date.strftime(
                "%d-%m-%Y"
            ),
            "house_lease_end_date": self.vn_house_lease_end_date,
            "created_at": self.vn_created_at.strftime("%d-%m-%Y"),
            "house_url": url_for("api.get_house", house_uuid=self.uuid, _external=True),
            "_links": {
                "owner_url": url_for("api.get_houseowner", owner_uuid=self.uuid),
                "tenant_url": url_for("api.get_house_tenant", house_uuid=self.uuid),
            },
        }
        return json_house

    def __str__(self):
        return self.vn_house_type

    def __repr__(self):
        return f"VNHouse({self.id}, {self.vn_house_type})"

    def house_disable(self):
        self.vn_house_is_open = False
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
        return VNHouse.query.filter_by(
            uuid=house_uuid, vn_user_id=current_user.id
        ).first()

    def lease_end_date(self):
        start_date = self.vn_house_lease_start_date
        notice_period = timedelta(days=15)
        due_date = start_date + timedelta(days=45) - notice_period
        return due_date


class VNTenant(DefaultUserInfoModel, TimestampMixin):

    """
    VNTenant
    Ce modèle représentera les locataires qui occupent les propriétés locatives.
    """

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
    vn_owner_id = db.Column(db.Integer, db.ForeignKey("houseowner.id"))

    payments = db.relationship(
        "VNPayment",
        lazy="dynamic",
        backref="tenant_payment",
        order_by="desc(VNPayment.vn_pay_date)",
    )

    def to_json(self):
        json_tenant = {
            "user_uuid": current_user.uuid,
            "tenant_uuid": self.uuid,
            "tenant_id": self.get_tenant_id(),
            "owner": self.tenants.to_json(),
            "house": self.house_tenant.to_json(),
            "gender": self.vn_gender,
            "fullname": self.vn_fullname,
            "addr_email": self.vn_addr_email,
            "profession": self.vn_profession,
            "parent_name": self.vn_parent_name,
            "card_number": self.vn_cni_number,
            "location": self.vn_location,
            "phonenumber_one": self.vn_phonenumber_one,
            "phonenumber_two": self.vn_phonenumber_two,
            "activated": self.vn_activated,
            "monthly_rent": self.get_monthly_rent(),
            "created_at": self.vn_created_at.strftime("%d-%m-%Y"),
            "_links": {
                "tenant_url": url_for("api.get_tenant", tenant_uuid=self.uuid),
            },
        }
        return json_tenant

    def __str__(self):
        return f"{self.vn_gender} {self.vn_fullname}"

    def __repr__(self):
        return f"VNTenant({self.id}, {self.vn_tenant_id})"

    def get_tenant_id(self):
        return f"#{self.vn_tenant_id}"

    @staticmethod
    def get_tenant_name(tenant):
        return tenant.vn_fullname

    @staticmethod
    def get_tenants_list():
        return VNTenant.query.filter_by(vn_user_id=current_user.id, vn_activated=True)

    @staticmethod
    def get_tenant(tenant_uuid):
        return VNTenant.query.filter_by(
            uuid=tenant_uuid, vn_user_id=current_user.id
        ).first()

    def get_monthly_rent(self):

        from src.payment import VNPayment

        today = date.today()
        mouth_rent = self.house_tenant.vn_house_rent
        due_date = self.house_tenant.vn_house_lease_end_date
        last_payment = self.payments.order_by(VNPayment.vn_pay_date.desc()).first()

        if due_date is None:
            return 0

        if today > due_date:
            days_late = (today - due_date).days
            if days_late < 15:
                rent_due = mouth_rent
            else:
                late_fee = mouth_rent * 0.1 * days_late
                rent_due = mouth_rent + late_fee
        else:
            rent_due = mouth_rent

        if (
            last_payment
            and last_payment.date.month == today.month
            and last_payment.date.year == today.year
        ):
            rent_due -= last_payment.vn_pay_amount

        if rent_due <= 0:
            return 0

        return rent_due
