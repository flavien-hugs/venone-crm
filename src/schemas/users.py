from src import ma

from src.auth.models import VNUser


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VNUser
        include_fk = True
        load_instance = True
        include_relationships = True


user_schema = UserSchema()
users_schema = UserSchema(many=True)
