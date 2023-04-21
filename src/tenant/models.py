from datetime import date
from datetime import datetime
from datetime import timedelta

from flask_login import current_user
from src import db
from src.mixins.models import DefaultUserInfoModel
from src.mixins.models import id_generator
from src.mixins.models import TimestampMixin
from src.payment import VNPayment


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
        order_by="desc(VNHouse.vn_created_at)",
    )
    tenants = db.relationship(
        "VNTenant",
        lazy="dynamic",
        backref="owner_tenants",
        order_by="desc(VNTenant.vn_created_at)",
    )
    payments = db.relationship(
        "VNPayment",
        lazy="dynamic",
        backref="owner_payment",
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
            "devise": current_user.vn_device,
            "amount_repaid": self.get_amount_repaid(),
            "amount": self.get_owner_property_values(),
            "total_percent": self.total_houses_amount(),
            "houses": [h.vn_house_id for h in self.houses],
            "tenants": [t.vn_tenant_id for t in self.tenants],
            "houses_list": [h.to_json() for h in self.houses],
            "tenants_list": [t.to_json() for t in self.tenants],
            "number_houses": self.houses.count(),
            "number_tenants": self.tenants.count(),
            "number_payments": self.payments.count(),
            "is_activated": self.vn_activated,
            "created_at": self.vn_created_at.strftime("%d-%m-%Y"),
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
        return f"{self.vn_fullname} - {self.vn_fullname} - {self.vn_phonenumber_one}"

    def __repr__(self):
        return f"VNHouseOwner({self.id}, {self.vn_fullname})"

    def get_owner_id(self):
        return f"#{self.vn_owner_id}"

    @staticmethod
    def get_houseowner_name(houseowner) -> str:
        return houseowner.vn_fullname

    def get_owner_available(self) -> bool:
        return "Compte actif" if self.vn_activated else "Compte inactif"

    @staticmethod
    def get_owners_list() -> list:
        query = VNHouseOwner.query.filter_by(
            vn_user_id=current_user.id, vn_activated=True
        )
        return query

    @staticmethod
    def get_owner(owner_uuid) -> dict:
        query = VNHouseOwner.query.filter_by(
            vn_user_id=current_user.id, uuid=owner_uuid
        )
        return query.first()

    @staticmethod
    def get_houses_list() -> list:
        query = VNHouse.query.filter_by(vn_user_id=current_user.id)
        return query

    @staticmethod
    def get_house(owner_uuid):
        query = VNHouse.query.filter_by(vn_user_id=current_user.id, uuid=owner_uuid)
        return query.first()

    @staticmethod
    def get_tenants(owner_uuid):
        query = VNTenant.query.filter_by(
            uuid=owner_uuid.uuid, vn_user_id=current_user.uuid
        )
        return query.first()

    @staticmethod
    def get_tenant(owner_uuid):
        query = VNTenant.query.filter_by(
            uuid=owner_uuid.uuid, vn_user_id=current_user.uuid
        )
        return query.first()

    def get_owner_property_values(self):
        user_houses = self.houses.filter_by(
            vn_house_is_open=True, vn_user_id=current_user.id
        ).all()
        total_house_value = sum(house.vn_house_rent for house in user_houses)
        return total_house_value

    def total_houses_amount(self):
        user_houses = self.houses.filter_by(
            vn_house_is_open=True, vn_user_id=current_user.id
        ).all()
        total = sum(house.get_house_rent_with_percentage() for house in user_houses)
        return total

    def get_amount_repaid(self):
        total = self.get_owner_property_values() - self.total_houses_amount()
        return total


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

    vn_house_lease_start_date = db.Column(
        db.Date, nullable=True, default=datetime.utcnow()
    )
    vn_house_lease_end_date = db.Column(
        db.Date, nullable=True, default=datetime.utcnow()
    )

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
            "owner_id": self.get_owner_id(),
            "tenant_id": self.get_current_tenant(),
            "user_uuid": current_user.uuid,
            "devise": current_user.vn_device,
            "house_id": self.get_house_id(),
            "house_type": self.vn_house_type,
            "house_rent": self.vn_house_rent,
            "house_month": self.vn_house_month,
            "house_guaranty": self.vn_house_guaranty,
            "house_number_room": self.vn_house_number_room,
            "house_address": self.vn_house_address,
            "house_is_open": self.vn_house_is_open,
            "house_status": self.get_house_open(),
            "house_percent": self.get_house_rent_with_percentage(),
            "house_lease_start_date": self.vn_house_lease_start_date.strftime(
                "%d-%m-%Y"
            ),
            "house_lease_end_date": self.vn_house_lease_end_date.strftime("%d-%m-%Y"),
        }
        return json_house

    def __str__(self) -> str:
        return f"{self.vn_house_id} - {self.vn_house_type} - {self.vn_house_rent}"

    def __repr__(self):
        return f"VNHouse({self.id}, {self.vn_house_type})"

    def house_disable(self):
        self.vn_house_is_open = False
        db.session.add(self)
        db.session.commit()

    def get_house_open(self) -> bool:
        return "indisponible" if self.vn_house_is_open else "disponible"

    def get_house_id(self) -> str:
        return f"#{self.vn_house_id}"

    @staticmethod
    def get_houses_list() -> list:
        houses = VNHouse.query.filter_by(vn_user_id=current_user.id)
        return houses

    @staticmethod
    def get_house(house_uuid) -> dict:
        house = VNHouse.query.filter_by(uuid=house_uuid, vn_user_id=current_user.id)
        return house.first()

    def get_owner_id(self):
        owners = VNHouseOwner.query.filter_by(
            id=self.vn_owner_id, vn_user_id=current_user.id
        )
        return next((own.get_owner_id() for own in owners), None)

    def get_house_tenants(self):
        house = VNHouse.query.filter_by(
            vn_user_id=current_user.id, vn_house_id=self
        ).first()
        return house.tenants

    def get_current_tenant(self):
        tenant = self.tenants[0] if len(self.tenants) > 0 else None
        return tenant.vn_fullname if tenant is not None else None

    def get_current_tenant_id(self):
        tenant = self.tenants[0] if len(self.tenants) > 0 else None
        return tenant.id if tenant is not None else None

    def get_tenant_phone_number(self):
        tenant = self.tenants[0] if len(self.tenants) > 0 else None
        return tenant.vn_phonenumber_one if tenant is not None else None

    def get_house_rent_with_percentage(self):
        if self.user_houses.vn_percentage is not None and self.user_houses.vn_percentage != 0:
            percent = self.user_houses.vn_percentage / 100
            result = self.vn_house_rent * percent
            return result
        else:
            return 0

    def update_lease_end_date(self):
        today = date.today()
        notice_period = timedelta(days=10)

        if today > self.vn_house_lease_end_date:
            next_month = (
                self.vn_house_lease_end_date.replace(day=28)
                + timedelta(days=31)
                - notice_period
            )
            self.vn_house_lease_end_date = next_month.replace(
                day=min(self.vn_house_lease_start_date.day, next_month.day)
            )
            db.session.add(self)
            db.session.commit()

    @staticmethod
    def process_payment_data(house, transaction_id):
        if house.vn_house_is_open:
            payment = VNPayment(
                vn_transaction_id=transaction_id,
                vn_pay_amount=house.vn_house_rent,
                vn_payee_id=house.vn_user_id,
                vn_owner_id=house.vn_owner_id,
                vn_tenant_id=house.get_current_tenant_id(),
                vn_house_id=house.id,
                vn_cinetpay_data={},
                vn_pay_date=datetime.utcnow().date(),
            )
            db.session.add(payment)
            db.session.commit()

    def is_rent_paid(self, tenant_id: int) -> bool:

        """
        Check if rent for the current month has been paid for a specific tenant
        """

        current_date = datetime.utcnow().date()
        current_year = current_date.year
        current_month = current_date.month

        rent_paid = (
            VNPayment.query.join(VNTenant)
            .join(VNHouse)
            .filter(
                VNPayment.vn_pay_status,
                VNTenant.id == tenant_id,
                db.extract("month", VNPayment.vn_pay_date) == current_month,
                db.extract("year", VNPayment.vn_pay_date) == current_year,
                VNHouse.id == self.id,
                VNHouse.vn_house_is_open,
            )
            .count()
        )

        return rent_paid > 0


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
            "devise": current_user.vn_device,
            "tenant_uuid": self.uuid,
            "owner": self.get_owner_id(),
            "tenant_id": self.get_tenant_id(),
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
            "payments": self.list_payments(),
            "created_at": self.vn_created_at.strftime("%d-%m-%Y"),
        }
        return json_tenant

    def __str__(self):
        return f"{self.id} {self.vn_fullname}"

    def __repr__(self):
        return f"VNTenant({self.id}, {self.vn_tenant_id})"

    def get_owner_id(self):
        owners = VNHouseOwner.query.filter_by(
            id=self.vn_owner_id, vn_user_id=current_user.id
        )
        return next((own.get_owner_id() for own in owners), None)

    def get_tenant_id(self) -> str:
        return f"#{self.vn_tenant_id}"

    @staticmethod
    def get_tenant_name(tenant) -> str:
        return tenant.vn_fullname

    @staticmethod
    def get_tenants_list() -> list:
        tenants = VNTenant.query.filter_by(vn_user_id=current_user.id)
        return tenants

    def list_payments(self):
        payments = self.payments.all()
        payments_json = [payment.to_json() for payment in payments]
        return payments_json

    @staticmethod
    def get_tenant(tenant_uuid) -> dict:
        tenant = VNTenant.query.filter_by(
            uuid=tenant_uuid, vn_user_id=current_user.id
        ).first()
        return tenant
