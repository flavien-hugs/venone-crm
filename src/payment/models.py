import logging
from datetime import date

from flask_login import current_user

from src.exts import db
from src.mixins.models import TimestampMixin, id_generator

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class VNPayment(TimestampMixin):
    __tablename__ = "payment"

    vn_payment_id = db.Column(
        db.String(5), nullable=True, unique=True, default=id_generator
    )
    vn_transaction_id = db.Column(db.String(10), nullable=True, unique=True)
    vn_pay_amount = db.Column(db.Float, nullable=False)
    vn_pay_late_penalty = db.Column(db.Float, nullable=True)
    vn_pay_date = db.Column(db.Date, nullable=False)
    vn_pay_status = db.Column(db.Boolean, default=False)
    vn_cinetpay_data = db.Column(db.JSON, default=False)

    vn_payee_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    vn_owner_id = db.Column(db.Integer, db.ForeignKey("houseowner.id"))
    owner = db.relationship(
        "VNHouseOwner",
        backref="owner_payment",
        order_by="desc(VNPayment.vn_pay_date)",
    )

    vn_tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"))
    tenant = db.relationship(
        "VNTenant",
        backref="tenant_payment",
        order_by="desc(VNPayment.vn_pay_date)",
    )

    vn_house_id = db.Column(db.Integer, db.ForeignKey("house.id"))
    house = db.relationship(
        "VNHouse", backref="house_payment", order_by="desc(VNPayment.vn_pay_date)"
    )

    def __str__(self):
        return self.vn_transaction_id

    def __repr__(self) -> str:
        return f"Payment(id={self.id!r}, fullname={self.vn_transaction_id!r}, {self.vn_pay_date})"

    @classmethod
    def paids(cls):
        return cls.query.filter_by(
            vn_payee_id=current_user.id, vn_pay_status=True
        ).order_by(cls.vn_created_at.desc())

    @classmethod
    def payments(cls):
        return db.select(cls).order_by(cls.vn_created_at.desc())

    @classmethod
    def unpaids(cls):
        return cls.query.filter_by(vn_pay_status=False).order_by(
            cls.vn_created_at.desc()
        )

    @classmethod
    def find_by_transaction_id(cls, transaction_id):
        return cls.query.filter_by(vn_transaction_id=transaction_id).first()

    def get_status_payment(self):
        return "payé" if self.vn_pay_status else "impayé"

    def calculate_late_penalty(self):
        today = date.today()
        days_late = ((today - self.house.vn_house_lease_end_date).days) + 3
        if days_late > 10 and not self.vn_pay_status:
            late_fee = self.house.vn_house_rent * 0.1
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
        return self.vn_trans_amount

    def __repr__(self):
        return f"VNTransferRequest({self.vn_transfer_id}, {self.vn_trans_status})"

    @classmethod
    def get_transfers_request(cls) -> list:
        transfers = cls.query.filter_by(vn_user_id=current_user.id)
        return transfers

    def get_status_transfer(self) -> bool:
        return "en cours" if self.vn_trans_status else "en cours"
