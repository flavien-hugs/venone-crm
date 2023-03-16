import random
import string
from datetime import date
from datetime import datetime
from datetime import timedelta

from flask_login import current_user
from src import db
from src.mixins.models import DefaultUserInfoModel
from src.mixins.models import TimestampMixin
from src.payment import VNPayment


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
            "amount": self.get_owner_property_values(),
            "houses": [h.vn_house_id for h in self.houses],
            "tenants": [t.vn_tenant_id for t in self.tenants],
            "number_houses": self.houses.count(),
            "number_tenants": self.tenants.count(),
            "number_payments": self.payments.count(),
            "is_activated": self.vn_activated,
            "created_at": self.vn_created_at.isoformat(),
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

    def get_owner_property_values(self) -> float:
        house_value = 0.0
        for house in self.houses.filter_by(vn_house_is_open=True):
            house_value += house.vn_house_rent
        return house_value


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
        lease_end_date = VNHouse.update_expired_lease_end_dates()
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
            "status_payment": self.get_status_payment(),
            "house_lease_start_date": self.vn_house_lease_start_date.strftime(
                "%d-%m-%Y"
            ),
            "house_lease_end_date": lease_end_date.strftime("%d-%m-%Y")
            if lease_end_date
            else self.vn_house_lease_end_date.strftime("%d-%m-%Y"),
        }
        return json_house

    def __str__(self):
        return self.vn_house_type

    def __repr__(self):
        return f"VNHouse({self.id}, {self.vn_house_type})"

    def house_disable(self):
        self.vn_house_is_open = False
        db.session.add(self)
        db.session.commit()

    def get_status_payment(self) -> bool:
        return "payé" if self.is_rent_paid() else "impayé"

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
        """
        liste des locataires de la propriété
        """
        house = VNHouse.query.filter_by(
            vn_user_id=current_user.id, vn_house_id=self
        ).first()
        return house.tenants

    def get_current_tenant(self):
        house = VNHouse.query.filter_by(id=self.id).first()
        for tenant in house.tenants:
            if tenant is None:
                return None
            return tenant.vn_fullname

    def get_tenant_phone_number(self):
        house = VNHouse.query.filter_by(id=self.id).first()
        for tenant in house.tenants:
            if tenant is None:
                return None
            return tenant.vn_phonenumber_one

    def is_rent_paid(tenant):
        """
        vérifie si le loyer du mois en cours
        avant la date d'échéance a été effectué ou pas
        """

        current_date = datetime.utcnow().date()
        current_year = current_date.year
        current_month = current_date.month

        last_payment = (
            VNHouse.query.join(VNPayment, VNHouse.id == VNPayment.vn_house_id)
            .filter(
                VNPayment.id == tenant.id,
                db.extract("month", VNPayment.vn_pay_date) < current_month,
                db.extract("year", VNPayment.vn_pay_date) < current_year,
            )
            .first()
        )

        return last_payment is not None and last_payment.payment_status

    def update_lease_end_date(self):
        today = date.today()
        notice_period = timedelta(days=15)

        if today > self.vn_house_lease_end_date:
            next_month = (
                self.vn_house_lease_end_date.replace(day=28)
                + timedelta(days=45)
                - notice_period
            )
            self.vn_house_lease_end_date = next_month.replace(
                day=min(self.vn_house_lease_start_date.day, next_month.day)
            )
            db.session.add(self)
            db.session.commit()

    @staticmethod
    def update_expired_lease_end_dates():

        today = date.today()

        expired_houses = VNHouse.query.filter(
            VNHouse.vn_house_is_open is True, VNHouse.vn_house_lease_end_date <= today
        ).all()

        for house in expired_houses:
            house.update_lease_end_date()
        db.session.commit()

    def get_missed_payments(self):
        today = date.today()
        if self.vn_house_lease_end_date < today:
            missed_payments = []
            for paid in self.payments:
                if paid.vn_pay_date > self.vn_house_lease_end_date:
                    missed_payments.append(paid)
            return missed_payments
        else:
            return []

    @staticmethod
    def tenants_paids():

        available_houses = VNHouse.query.filter(
            VNHouse.vn_house_is_open is True,
            VNHouse.vn_house_lease_end_date >= date.today(),
            VNHouse.vn_user_id == current_user.id,
        ).all()

        payments = [
            VNPayment.query.filter(
                VNPayment.vn_house_id == house.vn_house_id,
                VNPayment.vn_pay_date < house.vn_house_lease_end_date,
                VNPayment.vn_payee_id == current_user.id,
            ).all()
            for house in available_houses
        ]

        return payments

    @staticmethod
    def tenants_not_paid():
        """
        récupérer les locataires qui n'ont pas
        effectué de paiement pour le mois en cours
        """

        from src.auth.models import VNUser

        today = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        not_paid = (
            db.session.query(VNTenant)
            .join(VNPayment)
            .join(VNUser)
            .filter(VNTenant.vn_user_id == current_user.id)
            .filter(VNPayment.vn_pay_date < today)
            .filter(db.and_(VNPayment.vn_pay_date != VNHouse.vn_house_lease_start_date))
            .all()
        )
        return not_paid

    @staticmethod
    def tenants_paid():
        """
        récupérer les locataires qui ont
        effectué un paiement pour le mois en cours
        """

        current_month = date.today().month
        current_year = date.today().year

        paid = (
            db.session.query(VNTenant)
            .join(VNTenant.payments)
            .filter(
                VNTenant.vn_user_id == current_user.id,
                db.extract("month", VNPayment.vn_pay_date) == current_month,
                db.extract("year", VNPayment.vn_pay_date) == current_year,
            )
            .all()
        )
        return paid


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
            "monthly_rent": self.get_monthly_rent(),
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

    @staticmethod
    def get_tenant(tenant_uuid) -> dict:
        tenant = VNTenant.query.filter_by(
            uuid=tenant_uuid, vn_user_id=current_user.id
        ).first()
        return tenant

    def get_monthly_rent(self) -> float:

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
