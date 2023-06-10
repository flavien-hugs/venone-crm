import locale

from marshmallow import fields
from src.auth.models import VNUser
from src.exts import ma

from .houses import houses_schema
from .houses import payments_schema
from .houses import tenants_schema
from .houses import transfers_schema
from .owners import owners_schema


loc = locale.getlocale()
locale.setlocale(locale.LC_ALL, loc)


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VNUser
        include_fk = True
        load_instance = True
        include_relationships = True
        exclude = (
            "id",
            "vn_password",
        )

    is_admin = fields.Method("is_admin")
    vn_created_at = fields.DateTime(format="%d %B %Y")
    owner_percent = fields.Method("get_owner_percent")
    amount_apply_percent = fields.Method("amount_apply_percent")
    company_percent = fields.Method("get_company_percent")
    total_house_receive = fields.Method("total_houses_percent")
    total_house_amount = fields.Method("total_houses_amount")
    total_house_percent = fields.Method("get_amount_received")
    payments_count = fields.Method("get_payments_count")
    total_payment_month = fields.Method("total_payments_month")
    total_payments_received = fields.Method("get_total_payments_received")
    houses_count = fields.Method("get_houses_count")
    houses_close_count = fields.Method("get_houses_close_count")
    houses_open_count = fields.Method("get_houses_open_count")
    tenants_count = fields.Method("get_tenants_count")
    owners_count = fields.Method("get_houseowners_count")
    transfers_count = fields.Method("get_transfers_count")

    houses = fields.Method("get_houses")
    tenants = fields.Method("get_tenants")
    houseowners = fields.Method("get_owners")
    payments = fields.Method("get_payments")
    transfers = fields.Method("get_transfers")

    def is_admin(self, obj):
        return obj.is_administrator()

    def get_owner_percent(self, obj):
        return obj.get_owner_percent()

    def amount_apply_percent(self, obj):
        return obj.amount_apply_percent()

    def get_company_percent(self, obj):
        return obj.get_company_percent()

    def total_houses_percent(self, obj):
        return locale.format_string(
            "%.0f", obj.total_houses_percent(), grouping=True, monetary=True
        )

    def total_houses_amount(self, obj):
        return locale.format_string(
            "%.0f", obj.total_houses_amount(), grouping=True, monetary=True
        )

    def get_total_payments_received(self, obj):
        return locale.format_string(
            "%.0f", obj.get_total_payments_received(), grouping=True, monetary=True
        )

    def get_amount_received(self, obj):
        return locale.format_string(
            "%.0f", obj.get_amount_received(), grouping=True, monetary=True
        )

    def total_payments_month(self, obj):
        return locale.format_string(
            "%.0f", obj.total_payments_month(), grouping=True, monetary=True
        )

    def get_payments_count(self, obj):
        return obj.get_payments_count()
    
    def get_payments(self, obj):
        return payments_schema.dump(obj.get_payments_list())

    def get_transfers(self, obj):
        return transfers_schema.dump(obj.get_transfers_list())

    def get_transfers_count(self, obj):
        return obj.get_transfers_count()

    def get_houses(self, obj):
        return houses_schema.dump(obj.get_houses_list())

    def get_houses_count(self, obj):
        return obj.get_houses_count()

    def get_houses_close_count(self, obj):
        return obj.get_houses_close_count()

    def get_houses_open_count(self, obj):
        return obj.get_houses_open_count()

    def get_tenants(self, obj):
        return tenants_schema.dump(obj.get_tenants_list())

    def get_tenants_count(self, obj):
        return obj.get_tenants_count()

    def get_owners(self, obj):
        return owners_schema.dump(obj.get_houseowners_list())

    def get_houseowners_count(self, obj):
        return obj.get_houseowners_count()


user_schema = UserSchema()
users_schema = UserSchema(many=True)
