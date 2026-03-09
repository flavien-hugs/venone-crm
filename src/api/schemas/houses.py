from marshmallow import fields

from src.infrastructure.config.plugins import ma
from src.core import get_house_service
from src.infrastructure.persistence.models import (
    House,
    Payment,
    Tenant,
    TransferRequest,
)


class HouseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = House
        include_fk = True
        load_instance = True
        exclude = ("id", "vn_user_id", "vn_owner_id")

    id = fields.Integer(dump_only=True)
    house_id = fields.String(attribute="vn_house_id", dump_only=True)
    house_type = fields.String(attribute="vn_house_type", dump_only=True)
    house_rent = fields.Float(attribute="vn_house_rent", dump_only=True)
    house_guaranty = fields.Float(attribute="vn_house_guaranty", dump_only=True)
    house_month = fields.Integer(attribute="vn_house_month", dump_only=True)
    house_number_room = fields.Integer(attribute="vn_house_number_room", dump_only=True)
    house_address = fields.String(attribute="vn_house_address", dump_only=True)
    house_is_open = fields.Boolean(attribute="vn_house_is_open", dump_only=True)
    house_lease_start_date = fields.Date(
        attribute="vn_house_lease_start_date",
        dump_only=True,
        format="%d %B %Y",
    )
    house_lease_end_date = fields.Date(
        attribute="vn_house_lease_end_date",
        dump_only=True,
        format="%d %B %Y",
    )
    house_created_at = fields.DateTime(
        attribute="vn_created_at", dump_only=True, format="%d %B %Y"
    )
    house_status = fields.Method("get_house_status")

    def get_house_status(self, obj):
        house_service = get_house_service()
        return house_service.get_status_label(obj.id)


house_schema = HouseSchema()
houses_schema = HouseSchema(many=True)


class TenantSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tenant
        include_fk = True
        load_instance = True
        exclude = ("id", "vn_user_id", "vn_owner_id")

    id = fields.Integer(dump_only=True)
    tenant_id = fields.String(attribute="vn_tenant_id", dump_only=True)
    tenant_fullname = fields.String(attribute="vn_fullname", dump_only=True)
    tenant_phone_one = fields.String(attribute="vn_phonenumber_one", dump_only=True)
    tenant_phone_two = fields.String(attribute="vn_phonenumber_two", dump_only=True)
    tenant_cni_number = fields.String(attribute="vn_cni_number", dump_only=True)
    tenant_birthdate = fields.Date(
        attribute="vn_birthdate", dump_only=True, format="%d %B %Y"
    )
    tenant_created_at = fields.DateTime(
        attribute="vn_created_at", dump_only=True, format="%d %B %Y"
    )


tenant_schema = TenantSchema()
tenants_schema = TenantSchema(many=True)


class PaymentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Payment
        include_fk = True
        load_instance = True
        exclude = (
            "id",
            "vn_cinetpay_data",
            "vn_payee_id",
            "vn_owner_id",
            "vn_tenant_id",
            "vn_house_id",
        )

    vn_pay_date = fields.Date(format="%d %B %Y")
    vn_created_at = fields.DateTime(format="%d %B %Y")


payment_schema = PaymentSchema()
payments_schema = PaymentSchema(many=True)


class TransferRequestSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TransferRequest
        include_fk = True
        load_instance = True
        exclude = ("id", "vn_user_id")

    vn_created_at = fields.DateTime(format="%d %B %Y")


transfer_schema = TransferRequestSchema()
transfers_schema = TransferRequestSchema(many=True)
