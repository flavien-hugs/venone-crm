import random
import string
from datetime import date
from decimal import Decimal

from flask_login import current_user
from src import db
from src.mixins.models import TimestampMixin


def id_generator():
    return "".join(random.choices(string.digits, k=5))


class VNPayment(TimestampMixin):

    """
    VNPayment
    Ce modèle représentera les paiements individuels
    des loyers effectués par les locataires.
    """

    __tablename__ = "payment"

    vn_payment_id = db.Column(
        db.String(5), nullable=True, unique=True, default=id_generator
    )
    vn_transaction_id = db.db.Column(db.String(10), nullable=True, unique=True)
    vn_pay_amount = db.Column(db.Float, nullable=False)
    vn_pay_late_penalty = db.Column(db.Float, nullable=True)
    vn_pay_date = db.Column(db.Date, nullable=False)
    vn_pay_status = db.Column(db.Boolean, default=False)

    vn_payee_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    vn_owner_id = db.Column(db.Integer, db.ForeignKey("houseowner.id"))
    vn_tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"))
    vn_house_id = db.Column(db.Integer, db.ForeignKey("house.id"))

    def to_json(self):
        json_payment = {
            "user_uuid": current_user.uuid,
            "payment_uuid": self.uuid,
            "user_id": self.vn_payee_id,
            "owner_id": self.vn_owner_id,
            "tenant_id": self.vn_tenant_id,
            "house_id": self.vn_house_id,
            "amount": self.calculate_late_penalty(),
            "payment_date": self.vn_pay_date.strftime("%d-%m-%Y"),
            "payment_late_penalty": self.vn_pay_late_penalty,
            "payment_status": self.vn_pay_status,
            "house": self.house_payment.to_json(),
            "tenant": self.tenant_payment.to_json(),
            "make_payment": self.make_payment(),
            "payments": self.get_payments(),
            "payments_by_month": self.get_payments_by_month(),
            "payments_by_year": self.get_payments_by_year(),
            "outstanding_payments": self.get_outstanding_payments(),
            "total_payments": self.get_total_payments(),
            "created_at": self.vn_created_at.strftime("%d-%m-%Y"),
        }
        return json_payment

    def __str__(self):
        return self.vn_payment_id

    def __repr__(self):
        return f"Payment({self.id}, {self.vn_payment_id}, {self.vn_payment_date})"

    def calculate_late_penalty(self):
        today = date.today()
        days_late = ((today - self.house_payment.vn_house_lease_start_date).days) + 3
        if days_late > 10 and not self.vn_pay_status:
            late_fee = self.house_payment.vn_house_rent * Decimal(0.1)
            self.vn_pay_amount += late_fee
            self.vn_pay_late_penalty = late_fee
            db.session.commit()
        else:
            self.vn_pay_late_penalty = 0

    def make_payment(self) -> bool:
        self.vn_pay_status = True
        db.session.commit()

    def get_payments(self):
        # A method that creates a new rent payment
        # record for the given tenant_id and amount.
        pass

    def get_payments_by_month(self):
        # A method that retrieves all rent payment records
        # for the given tenant_id in the specified month and year.
        pass

    def get_payments_by_year(self, year):
        # A method that retrieves all rent payment
        # records for the given tenant_id in the specified year
        pass

    def get_outstanding_payments(self):
        # A method that retrieves all rent payment
        # records for the given tenant_id that have not been fully paid.
        pass

    def get_total_payments(self):
        #  A method that retrieves the total
        # amount of rent payments made by the given tenant_id.
        pass
