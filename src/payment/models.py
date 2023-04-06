import logging
from datetime import date

from cinetpay_sdk.s_d_k import Cinetpay
from flask import current_app
from flask_login import current_user
from src import db
from src.mixins.models import id_generator
from src.mixins.models import TimestampMixin

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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
    vn_cinetpay_data = db.Column(db.JSON, default=False)

    vn_payee_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    vn_owner_id = db.Column(db.Integer, db.ForeignKey("houseowner.id"))
    vn_tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"))
    vn_house_id = db.Column(db.Integer, db.ForeignKey("house.id"))

    def to_json(self):
        json_payment = {
            "payment_uuid": self.uuid,
            "user_id": self.vn_payee_id,
            "owner_id": self.vn_owner_id,
            "tenant_id": self.vn_tenant_id,
            "house_id": self.vn_house_id,
            "payment_id": self.vn_payment_id,
            "trans_id": self.vn_transaction_id,
            "house_rent": self.vn_pay_amount,
            "house": self.house_payment.to_json(),
            "trans_info": self.vn_cinetpay_data,
            "amount_penalty": self.calculate_late_penalty(),
            "payment_date": self.vn_pay_date.strftime("%d-%m-%Y"),
            "payment_late_penalty": self.vn_pay_late_penalty,
            "payment_status": self.vn_pay_status,
            "get_payment": self.get_status_payment(),
            "created_at": self.vn_created_at.strftime("%d-%m-%Y"),
            "check_info_trans": self.check_transaction_trx(),
        }
        return json_payment

    def __str__(self):
        return self.vn_payment_id

    def __repr__(self):
        return f"Payment({self.id}, {self.vn_payment_id}, {self.vn_payment_date})"

    @staticmethod
    def get_payment_list() -> list:
        payments = VNPayment.query.filter_by(vn_payee_id=current_user.id)
        return payments

    def check_transaction_trx(self):
        try:
            app = current_app._get_current_object()
            SITEID = app.config["CINETPAY_SITE_ID"]
            APIKEY = app.config["CINETPAY_API_KEY"]
            client = Cinetpay(APIKEY, SITEID)

            response_data = client.TransactionVerfication_trx(self.vn_transaction_id)

            if (
                response_data["code"] == "00"
                and response_data["data"]["status"] == "ACCEPTED"
            ):
                payment = VNPayment.query.filter_by(
                    vn_transaction_id=self.vn_transaction_id
                ).first()
                if payment:
                    payment.vn_pay_status = True
                    payment.vn_cinetpay_data = response_data
                    db.session.commit()
        except Exception as e:
            logger.warning(
                f"Error verifying transaction with id {self.vn_transaction_id}: {e}"
            )

    def get_status_payment(self) -> bool:
        return "payé" if self.vn_pay_status else "impayé"

    def calculate_late_penalty(self):
        today = date.today()
        days_late = ((today - self.house_payment.vn_house_lease_end_date).days) + 3
        if days_late > 10 and not self.vn_pay_status:
            late_fee = self.house_payment.vn_house_rent * 0.1
            self.vn_pay_amount += late_fee
            self.vn_pay_late_penalty = late_fee
            db.session.commit()
        else:
            self.vn_pay_late_penalty = 0
