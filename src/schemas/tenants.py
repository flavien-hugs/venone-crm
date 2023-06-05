from src import ma

from src.tenant.models import VNTenant


class VNTenantSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VNTenant
        include_fk = True
        load_instance = True
        include_relationships = True


tenant_schema = VNTenantSchema()
tenants_schema = VNTenantSchema(many=True)
