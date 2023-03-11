import random
import string
from datetime import datetime, date
from decimal import Decimal

import requests
from cinetpay_sdk.s_d_k import Cinetpay
from flask import current_app
from flask_login import current_user
from src import db
from src.mixins.models import TimestampMixin

from src.auth.models import VNUser
from src.tenant.models import VNTenant, VNHouse


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

    @staticmethod
    def tenants_paid():
        # récupérer les locataires qui ont
        # effectué un paiement pour le mois en cours

        current_month = date.today().month
        current_year = date.today().year

        paid = db.session.query(VNTenant)\
            .join(VNTenant.payments)\
            .filter(
                VNTenant.vn_payee_id == current_user.id,
                db.extract('month', VNPayment.vn_pay_date) == current_month,
                db.extract('year', VNPayment.vn_pay_date) == current_year,
            ).all()

        return paid

    @staticmethod
    def tenants_paids():
        available_houses = VNHouse.query.filter(
            VNHouse.vn_house_is_open == True,
            VNHouse.vn_house_lease_end_date >= date.today(),
            VNHouse.vn_user_id == current_user.id
        ).all()

        print(available_houses)

        payments = [
            VNPayment.query.filter(
                VNPayment.vn_house_id == house.vn_house_id,
                VNPayment.vn_pay_date < house.vn_house_lease_end_date,
                VNPayment.vn_payee_id == current_user.id
            ).all() for house in available_houses
        ]

        print(payments)

        return payments

    @staticmethod
    def tenants_not_paid():
        # récupérer les locataires qui n'ont pas
        # effectué de paiement pour le mois en cours

        today = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        not_paid = db.session.query(VNTenant)\
            .join(VNPayment).join(VNUser)\
            .filter(VNTenant.vn_payee_id == current_user.id)\
            .filter(VNPayment.vn_pay_date < today)\
            .filter(db.and_(VNPayment.vn_pay_date != VNHouse.vn_house_lease_start_date)).all()
        return not_paid

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

    def make_payment(self):
        self.vn_pay_status = True
        db.session.commit()

    def get_payments(amount, tenant_id):
        # A method that creates a new rent payment
        # record for the given tenant_id and amount.
        pass

    def get_payments_by_month(tenant_id, month, year):
        # A method that retrieves all rent payment records
        # for the given tenant_id in the specified month and year.
        pass

    def get_payments_by_year(tenant_id, year):
        # A method that retrieves all rent payment
        # records for the given tenant_id in the specified year
        pass

    def get_outstanding_payments(tenant_id):
        # A method that retrieves all rent payment
        # records for the given tenant_id that have not been fully paid.
        pass

    def get_total_payments(tenant_id):
        #  A method that retrieves the total
        # amount of rent payments made by the given tenant_id.
        pass

    def generate_payment_token(self):

        API_KEY = current_app.config["CINETPAY_API_KEY"]
        SITE_ID = current_app.config["CINETPAY_SITE_ID"]

        client = Cinetpay(API_KEY, SITE_ID)

        data = {
            "amount": self.vn_pay_amount,
            "currency": "XOF",
            "transaction_id": self.vn_payment_id,
            "description": f"Paiement du loyer {tenant.house.vn_house_id}",
            "return_url": "https://venone.app",
            "notify_url": "https://venone.app",
            "customer_surname": self.tenant.vn_fullname,
        }

        response = client.PaymentInitialization(data)

        if response.status_code != 200:
            return None

        payment_url = response["data"]["payment_url"]
        return payment_url

    def send_payment_link(payment_url, tenant_id):

        SMS_APIKEY = current_app.config["SMS_API_KEY"]
        SMS_SENDER_ID = current_app.config["SENDER_ID"]

        tenant = VNTenant.query.get(tenant_id)

        phone_number = tenant.vn_phonenumber_one
        message = f"""
        Bonjour {tenant.vn_fullname}, Votre loyer du mois
        précédent est prêt. Veuillez cliquer sur ce lien:
        {payment_url} pour procéder au paiement.
        """
        sms_url = f"https://sms.lws.fr/sms/api?action=send-sms&api_key={SMS_APIKEY}\
            &to={phone_number}&from={SMS_SENDER_ID}&sms={message}"

        response = requests.post(sms_url)

        if response.status_code != 200:
            return False

        return True
