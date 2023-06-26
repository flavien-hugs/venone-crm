import locale
from datetime import date
from datetime import datetime
from datetime import timedelta

from flask_login import current_user
from src.exts import db
from src.mixins.models import DefaultUserInfoModel
from src.mixins.models import id_generator
from src.mixins.models import TimestampMixin
from src.payment import VNPayment


loc = locale.getlocale()
locale.setlocale(locale.LC_ALL, loc)


class VNHouseOwner(DefaultUserInfoModel, TimestampMixin):
    __tablename__ = "houseowner"

    vn_owner_id = db.Column(
        db.String(5), nullable=True, unique=True, default=id_generator
    )
    vn_avatar = db.Column(db.String(80), nullable=True)
    vn_user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="cascade"))
    vn_owner_percent = db.Column(db.Float, default=0, nullable=True)

    def __str__(self):
        return f"{self.vn_fullname} - {self.vn_fullname} - {self.vn_phonenumber_one}"

    def __repr__(self):
        return f"VNHouseOwner({self.id}, {self.vn_fullname})"

    def get_owner_id(self):
        return f"#{self.vn_owner_id}"

    @classmethod
    def get_owners_list(cls):
        return (
            db.select(cls)
            .where(cls.vn_user_id == current_user.id)
            .order_by(cls.vn_created_at.desc())
        )

    def get_owner_houses(self):
        houses = VNHouse.query.filter(
            VNHouse.vn_house_is_open == True,
            VNHouse.vn_user_id == current_user.id,
            VNHouse.vn_owner_id == self.id,
        ).all()
        return houses

    def get_owner_property_values(self):
        houses = self.get_owner_houses()
        total_house_value = sum(house.vn_house_rent for house in houses)
        return total_house_value

    def total_houses_amount(self):
        houses = self.get_owner_houses()
        total = sum(house.get_house_rent_with_percent() for house in houses)
        return total

    def get_amount_repaid(self):
        return self.get_owner_property_values() - self.total_houses_amount()

    def get_houses_count(self):
        return len(self.get_owner_houses())

    def get_owner_tenants(self):
        tenants = VNTenant.query.filter(
            VNTenant.vn_user_id == current_user.id, VNTenant.vn_owner_id == self.id
        ).all()
        return tenants

    def get_tenants_count(self):
        return len(self.get_owner_tenants())

    def get_owner_payments(self):
        payments = VNPayment.query.filter(
            VNPayment.vn_payee_id == current_user.id, VNPayment.vn_owner_id == self.id
        ).all()
        return payments


class VNHouse(TimestampMixin):
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
    owner = db.relationship(
        "VNHouseOwner",
        backref="owner_houses",
        order_by="desc(VNHouse.vn_created_at)",
    )

    def __str__(self) -> str:
        return f"{self.vn_house_id} - {self.vn_house_type} - {self.vn_house_rent}"

    def __repr__(self) -> str:
        return f"VNHouse({self.id}, {self.vn_house_type})"

    def get_remaining_days(self):
        lease_end_date = self.vn_house_lease_end_date
        current_date = datetime.utcnow().date()
        remaining_days = (lease_end_date - current_date).days
        return remaining_days

    def house_disable(self):
        self.vn_house_is_open = False
        db.session.add(self)
        db.session.commit()

    def get_house_open(self):
        return "indisponible" if self.vn_house_is_open else "disponible"

    def get_house_id(self) -> str:
        return f"#{self.vn_house_id}"

    @staticmethod
    def get_available_houses(cls, uuid):
        return cls.query.filter_by(vn_house_id=uuid, vn_house_is_open=False).first()

    @classmethod
    def get_houses_list(cls) -> list:
        return (
            db.select(cls)
            .where(cls.vn_user_id == current_user.id)
            .order_by(cls.vn_created_at.desc())
        )

    @classmethod
    def get_house_object(cls, uuid) -> dict:
        return cls.query.filter_by(uuid=uuid, vn_user_id=current_user.id).first()

    def get_house_owner(self):
        house_owner = self.owner
        return house_owner.vn_owner_id if house_owner is not None else None

    def get_current_tenant(self):
        tenant = self.house_tenants[0] if self.house_tenants else None
        return tenant.vn_fullname if tenant is not None else None

    def get_current_tenant_id(self):
        tenant = self.house_tenants[0] if self.house_tenants else None
        return tenant.id if tenant is not None else None

    def get_tenant_phone_number(self):
        tenant = self.house_tenants[0] if self.house_tenants else None
        return tenant.vn_phonenumber_one if tenant is not None else None

    def get_house_rent_with_percent(self):
        if (
            self.owner
            and self.owner.vn_owner_percent is not None
            and self.owner.vn_owner_percent != 0
        ):
            percent = self.owner.vn_owner_percent / 100
            if percent != 0:
                result = self.vn_house_rent * percent
                return result
        return 0

    def update_lease_end_date(self):
        today = date.today()
        notice_period = timedelta(days=10)

        if today >= self.vn_house_lease_end_date:
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
        "VNHouse",
        uselist=False,
        backref="house_tenants",
        order_by="desc(VNTenant.vn_created_at)",
    )

    vn_owner_id = db.Column(db.Integer, db.ForeignKey("houseowner.id"))
    owner = db.relationship(
        "VNHouseOwner",
        backref="owner_tenants",
        order_by="desc(VNTenant.vn_created_at)",
    )

    def __str__(self):
        return f"{self.id} {self.vn_fullname}"

    def __repr__(self) -> str:
        return f"VNTenant({self.id}, {self.vn_tenant_id})"

    def get_tenant_id(self) -> str:
        return f"#{self.vn_tenant_id}"

    def get_tenant_owner(self):
        tenant_owner = self.owner
        return tenant_owner.vn_owner_id if tenant_owner is not None else None

    @classmethod
    def get_tenants_list(cls) -> list:
        tenants = cls.query.filter_by(vn_user_id=current_user.id)
        return tenants

    def get_payment_history(self) -> list:
        payments = VNPayment.query\
            .filter_by(vn_tenant_id=self.id, vn_pay_status=True)\
            .order_by(VNPayment.vn_pay_date.desc()).all()
        return payments
