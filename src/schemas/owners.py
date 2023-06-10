import locale

from marshmallow import fields
from src.exts import ma
from src.tenant.models import VNHouseOwner

from .houses import houses_schema
from .houses import payments_schema
from .houses import tenants_schema


loc = locale.getlocale()
locale.setlocale(locale.LC_ALL, loc)


class VNHouseOwnerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VNHouseOwner
        include_fk = True
        load_instance = True
        include_relationships = True
        exclude = ("id", "vn_user_id")

    owner_houses = fields.Method("get_owner_houses")
    owner_tenants = fields.Method("get_owner_tenants")
    owner_payments = fields.Method("get_owner_payments")

    devise = fields.Method("get_devise")
    amount_repaid = fields.Method("get_amount_repaid")
    amount = fields.Method("get_owner_property_values")
    total_percent = fields.Method("get_total_houses_amount")
    number_tenants = fields.Method("tenants_count")
    number_houses = fields.Method("houses_count")
    vn_created_at = fields.DateTime(format="%d %B %Y")

    def get_owner_houses(self, obj):
        return houses_schema.dump(obj.get_owner_houses())

    def get_owner_tenants(self, obj):
        return tenants_schema.dump(obj.get_owner_tenants())

    def get_owner_payments(self, obj):
        return payments_schema.dump(obj.get_owner_payments())

    def get_devise(self, obj):
        return obj.house_owner.vn_device

    def get_amount_repaid(self, obj):
        return locale.format_string(
            "%.0f", obj.get_amount_repaid(), grouping=True, monetary=True
        )

    def get_owner_property_values(self, obj):
        return locale.format_string(
            "%.0f", obj.get_owner_property_values(), grouping=True, monetary=True
        )

    def get_total_houses_amount(self, obj):
        return locale.format_string(
            "%.0f", obj.total_houses_amount(), grouping=True, monetary=True
        )

    def houses_count(self, obj):
        return obj.get_houses_count()

    def tenants_count(self, obj):
        return obj.get_tenants_count()


owner_schema = VNHouseOwnerSchema()
owners_schema = VNHouseOwnerSchema(many=True)
