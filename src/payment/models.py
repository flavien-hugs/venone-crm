import logging
from datetime import date

from cinetpay_sdk.s_d_k import Cinetpay
from flask import current_app
from flask_login import current_user
from src.exts import db
from src.mixins.models import id_generator
from src.mixins.models import TimestampMixin

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class VNPayment(TimestampMixin):

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
            "house": self.get_payment_house_info(),
            "trans_info": self.vn_cinetpay_data,
            # "amount_penalty": self.calculate_late_penalty(),
            "payment_date": self.vn_pay_date.strftime("%d-%m-%Y"),
            "payment_late_penalty": self.vn_pay_late_penalty,
            "payment_status": self.vn_pay_status,
            "get_payment": self.get_status_payment(),
            "created_at": self.vn_created_at.strftime("%d-%m-%Y"),
            # "check_info_trans": self.check_transaction_trx()
        }
        return json_payment

    def __str__(self):
        return self.vn_transaction_id

    def __repr__(self):
        return f"Payment({self.vn_transaction_id}, {self.vn_payment_id}, {self.vn_pay_date})"

    @classmethod
    def get_payment_house_info(cls):
        from src.tenant import VNHouse
        house = VNHouse.query.filter_by(id=cls.vn_house_id, vn_user_id=cls.vn_payee_id).first()
        return house.to_json() if house is not None else None

    @classmethod
    def get_payments(cls):
        return cls.query.filter_by(vn_payee_id=current_user.id, vn_pay_status=True)

    @classmethod
    def find_by_transaction_id(cls, vn_transaction_id):
        return cls.query.filter_by(vn_transaction_id=vn_transaction_id).first()

    @classmethod
    def check_transaction_trx(cls):
        try:
            current_app_obj = current_app._get_current_object()
            SITEID = current_app_obj.config["CINETPAY_SITE_ID"]
            APIKEY = current_app_obj.config["CINETPAY_API_KEY"]
            client = Cinetpay(APIKEY, SITEID)

            payments = cls.get_payments()

            for payment in payments:
                payment_id = cls.find_by_transaction_id(payment)
                response_data = client.TransactionVerfication_trx(payment_id)
                logger.info("response data: %s", response_data)

                if isinstance(response_data, dict):
                    if (
                        response_data["code"] == "00"
                        and response_data["data"]["status"] == "ACCEPTED"
                    ):
                        payment.vn_pay_status = True
                        payment.vn_cinetpay_data = response_data
                        db.session.commit()
                    elif (
                        response_data["code"] == "662"
                        and response_data["message"] == "WAITING_CUSTOMER_PAYMENT"
                        and response_data["data"]["status"] == "PENDING"
                    ):
                        payment.vn_pay_status = False
                        payment.vn_cinetpay_data = response_data
                        db.session.commit()
                    else:
                        logger.warning(
                            "Invalid response data for transaction ID %s: %s",
                            payment.id,
                            response_data,
                        )
                else:
                    logger.warning(
                        "Invalid response data type for transaction ID %s: %s",
                        payment.id,
                        type(response_data),
                    )
        except Exception as e:
            logger.warning("Error processing transaction: %s", e)

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


class VNTransferRequest(TimestampMixin):

    __tablename__ = "transfer_request"

    vn_transfer_id = db.Column(
        db.String(5), nullable=True, unique=True, default=id_generator
    )
    vn_user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    vn_trans_amount = db.Column(db.Float, nullable=False)
    vn_trans_status = db.Column(db.Boolean, default=False)
    vn_withdrawal_number = db.Column(db.String(50), nullable=True)
    vn_withdrawal_method = db.Column(db.String(50), nullable=True)
    vn_cinetpay_data = db.Column(db.JSON, default=False)

    def __str__(self):
        return self.vn_user_id

    def to_json(self):
        data = {
            "transfer_uuid": self.uuid,
            "transfer_id": self.vn_transfer_id,
            "amount": "{:,.2f}".format(self.vn_trans_amount),
            "status": self.vn_trans_status,
            "message": self.get_status_transfer(),
            "withdrawal_number": self.vn_withdrawal_number,
            "withdrawal_method": self.vn_withdrawal_method,
            "created_at": self.vn_created_at.strftime("%d-%m-%Y"),
        }
        return data

    def __repr__(self):
        return f"VNTransferRequest({self.id}, {self.vn_trans_amount}, {self.vn_trans_status})"

    @classmethod
    def get_transfers_request(cls) -> list:
        transfers = cls.query.filter_by(vn_user_id=current_user.id)
        return transfers

    def get_status_transfer(self) -> bool:
        return "en cours" if self.vn_trans_status else "en cours"
