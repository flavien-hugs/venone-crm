from src import ma


class UserSchema(ma.Schema):
    class Meta:
        fields = ("vn_addr_email", "vn_fullname", "_links")

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api.user_detail", values=dict(id="<id>")),
            "collection": ma.URLFor("api.users_all"),
        }
    )


user_schema = UserSchema()
users_schema = UserSchema(many=True)
