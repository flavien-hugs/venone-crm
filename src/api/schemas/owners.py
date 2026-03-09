from marshmallow import fields
from src.infrastructure.config.plugins import ma
from src.infrastructure.persistence.models import HouseOwner
from src.infrastructure.shared.helpers import formatted_number


class HouseOwnerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = HouseOwner
        include_fk = True
        load_instance = True
        exclude = ("id", "vn_user_id")

    id = fields.Integer(dump_only=True)
    fullname = fields.String(attribute="vn_fullname", dump_only=True)
    gender = fields.String(attribute="vn_gender", dump_only=True)
    owner_id = fields.String(attribute="vn_owner_id", dump_only=True)
    owner_percent = fields.Method("get_owner_percent")
    phonenumber_one = fields.String(attribute="vn_phonenumber_one", dump_only=True)
    phonenumber_two = fields.String(attribute="vn_phonenumber_two", dump_only=True)
    cni_number = fields.String(attribute="vn_cni_number", dump_only=True)
    created_at = fields.DateTime(
        attribute="vn_created_at", dump_only=True, format="%d %B %Y"
    )

    def get_owner_percent(self, obj):
        return formatted_number(obj.vn_owner_percent or 0.0)

owner_schema = HouseOwnerSchema()
owners_schema = HouseOwnerSchema(many=True)
