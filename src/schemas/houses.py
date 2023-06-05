from src import ma

from src.tenant.models import VNHouse


class VNHouseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VNHouse
        include_fk = True
        load_instance = True
        include_relationships = True


house_schema = VNHouseSchema()
houses_schema = VNHouseSchema(many=True)
