from marshmallow import fields
from src.exts import ma
from src.payment import VNPayment
from src.payment import VNTransferRequest
from src.tenant.models import VNHouse
from src.tenant.models import VNTenant


class VNHouseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VNHouse
        include_fk = True
        load_instance = True
        exclude = ("id", "vn_user_id", "vn_owner_id")

    devise = fields.Method("get_devise")
    house_status = fields.Method("get_house_status")
    owner = fields.Method("get_house_owner")
    tenant = fields.Method("get_tenant")
    house_percent = fields.Method("get_house_percent")
    remaining_days = fields.Method("get_remaining_days")
    vn_created_at = fields.DateTime(format="%d %B %Y")
    vn_house_lease_end_date = fields.DateTime(format="%d %B %Y")
    vn_house_lease_start_date = fields.DateTime(format="%d %B %Y")

    def get_devise(self, obj):
        return obj.user_houses.vn_device

    def get_remaining_days(self, obj):
        return obj.get_remaining_days()

    def get_house_status(self, obj):
        return obj.get_house_open()

    def get_tenant(self, obj):
        return obj.get_current_tenant()

    def get_house_owner(self, obj):
        return obj.get_house_owner()

    def get_house_percent(self, obj):
        return obj.get_house_rent_with_percent()


house_schema = VNHouseSchema()
houses_schema = VNHouseSchema(many=True)


class VNTenantSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VNTenant
        include_fk = True
        load_instance = True
        exclude = ("id", "vn_user_id", "vn_owner_id")

    owner = fields.Method("get_tenant_owner")
    house = fields.Nested(house_schema)
    vn_created_at = fields.DateTime(format="%d %B %Y")

    def get_tenant_owner(self, obj):
        return obj.get_tenant_owner()


tenant_schema = VNTenantSchema()
tenants_schema = VNTenantSchema(many=True)


class VNPaymentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VNPayment
        include_fk = True
        load_instance = True
        exclude = (
            "id",
            "vn_payee_id",
            "vn_house_id",
            "vn_owner_id",
            "vn_tenant_id",
        )

    vn_created_at = fields.DateTime(format="%d %B %Y")
    payment_status = fields.Method("get_payment_status")
    check_info_trans = fields.Method("check_info_trans")
    house = fields.Nested(house_schema)
    tenant = fields.Nested(tenant_schema)

    def check_info_trans(self, obj):
        return obj.check_info_trans()

    def get_payment_status(self, obj):
        return obj.get_status_payment()


payment_schema = VNPaymentSchema()
payments_schema = VNPaymentSchema(many=True)


class VNTransferRequestSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VNTransferRequest
        include_fk = True
        load_instance = True
        exclude = ("id", "vn_user_id")

    vn_created_at = fields.DateTime(format="%d %B %Y")


transfer_schema = VNTransferRequestSchema()
transfers_schema = VNTransferRequestSchema(many=True)
