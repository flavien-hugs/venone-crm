from src import ma

from src.payment import VNPayment, VNTransferRequest


class VNPaymentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VNPayment
        include_fk = True
        load_instance = True
        include_relationships = True


payment_schema = VNPaymentSchema()
payments_schema = VNPaymentSchema(many=True)


class VNTransferRequestSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VNTransferRequest
        include_fk = True
        load_instance = True
        include_relationships = True


transfert_schema = VNTransferRequestSchema()
transferts_schema = VNTransferRequestSchema(many=True)
