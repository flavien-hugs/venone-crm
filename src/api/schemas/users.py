from marshmallow import fields

from src.core import get_user_service
from src.infrastructure.config.plugins import ma
from src.infrastructure.persistence.models import User
from src.infrastructure.shared.helpers import formatted_number


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True
        load_instance = True
        include_relationships = True
        exclude = (
            "id",
            "vn_password",
            "vn_house_owner",
            "vn_role_id",
            "vn_company",
            "vn_balance",
            "vn_last_seen",
        )

    fullname = fields.String(attribute="vn_fullname", dump_only=True)
    addr_email = fields.String(attribute="vn_addr_email", dump_only=True)
    phonenumber_one = fields.String(attribute="vn_phonenumber_one", dump_only=True)
    cni_number = fields.String(attribute="vn_cni_number", dump_only=True)
    country = fields.String(attribute="vn_country", dump_only=True)
    avatar = fields.String(attribute="vn_avatar", dump_only=True)
    birthdate = fields.String(attribute="vn_birthdate", dump_only=True)
    find_us = fields.String(attribute="vn_find_us", dump_only=True)
    ip_address = fields.String(attribute="vn_ip_address", dump_only=True)
    device = fields.String(attribute="vn_device", dump_only=True)
    agencie_name = fields.String(attribute="vn_agencie_name", dump_only=True)
    business_number = fields.String(attribute="vn_business_number", dump_only=True)

    created_at = fields.DateTime(
        attribute="vn_created_at", dump_only=True, format="%d %B %Y"
    )
    balance = fields.Method("get_balance")
    total_payments = fields.Method("get_total_payments")
    monthly_payments = fields.Method("get_monthly_payments")
    amount_apply_percent = fields.Method("get_amount_apply_percent")
    total_houses_amount = fields.Method("get_total_houses_amount")
    total_amount_of_houses = fields.Method("get_total_amount_of_houses")
    dashboard_stats = fields.Method("get_dashboard_stats")

    def get_balance(self, obj):
        return formatted_number(obj.vn_balance or 0.0)

    def get_total_payments(self, obj):
        user_service = get_user_service()
        return formatted_number(user_service.get_total_payments_received(obj.id))

    def get_monthly_payments(self, obj):
        user_service = get_user_service()
        return formatted_number(user_service.get_user_monthly_payments(obj.id))

    def get_amount_apply_percent(self, obj):
        user_service = get_user_service()
        return formatted_number(user_service.calculate_amount_apply_percent(obj.id))

    def get_total_houses_amount(self, obj):
        user_service = get_user_service()
        return formatted_number(user_service.calculate_total_houses_amount(obj.id))

    def get_total_amount_of_houses(self, obj):
        user_service = get_user_service()
        return formatted_number(user_service.calculate_total_amount_of_houses(obj.id))

    def get_dashboard_stats(self, obj):
        user_service = get_user_service()
        return user_service.get_dashboard_stats(obj.id)


user_schema = UserSchema()
users_schema = UserSchema(many=True)
