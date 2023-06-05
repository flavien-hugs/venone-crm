from src import ma

from src.tenant.models import VNHouseOwner


class VNHouseOwnerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VNHouseOwner
        include_fk = True
        load_instance = True
        include_relationships = True


owner_schema = VNHouseOwnerSchema()
owners_schema = VNHouseOwnerSchema(many=True)
