from flask_restx import reqparse, fields, inputs

from .. import api


signup_house_owner_resource_fields = api.model(
    "AuthHouseOwnerSignup",
    {
        "vn_user_gender": fields.String(required=True, description="The user gender"),
        "vn_user_fullname": fields.String(required=True, description="The user fullname"),
        "vn_user_addr_email": fields.String(required=True, description="The user adresse email"),
        "vn_user_cni_number": fields.String(required=True, description="The user card identity number"),
        "vn_user_phonenumber_one": fields.String(required=True, description="The user phone number"),
        "vn_user_country": fields.String(required=True, description="The user country"),
        "vn_user_password": fields.String(required=True, description="The user password"),
    },
)


login_resource_fields = api.model(
    "AuthLogin",
    {
        "vn_user_addr_email": fields.String(required=True, description="The user adresse email"),
        "vn_user_password": fields.String(required=True, description="The user password"),
    },
)
