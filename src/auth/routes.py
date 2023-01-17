from http import HTTPStatus

from flask import request, jsonify, make_response
from flask_restx import Resource
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    create_refresh_token,
)

from .. import api
from .models import VNUser
from .constants import AccountType
from .resources import signup_house_owner_resource_fields, login_resource_fields

auth_ns = api.namespace(
    "auth", version="1.0", description="A namespace for user authentication"
)


PASSWORD_LENGTH = 6
FULLNAME_LENGTH = 4


@auth_ns.route("/ownerhouse/signup", strict_slashes=False)
class AuthHouseOwnerSignup(Resource):
    @auth_ns.response(int(HTTPStatus.CREATED), "New user was successfully created.")
    @auth_ns.response(int(HTTPStatus.CONFLICT), "Email address is already registered.")
    @auth_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @auth_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    @auth_ns.expect(signup_house_owner_resource_fields)
    @auth_ns.doc(body=signup_house_owner_resource_fields)
    def post(self):
        """Register a user owner house and return an user"""
        data = request.get_json()
        gender = data["vn_user_gender"]
        fullname = data["vn_user_fullname"]
        addr_email = data["vn_user_addr_email"]
        cni_number = data["vn_user_cni_number"]
        phonenumber = data["vn_user_phonenumber_one"]
        country = data["vn_user_country"]
        password = data["vn_user_password"]

        if len(password) < PASSWORD_LENGTH:
            return jsonify({"message": "Password is too short"}), int(HTTPStatus.BAD_REQUEST)

        if len(fullname) < FULLNAME_LENGTH:
            return (
                jsonify(
                    {"message": f"This user fullname '{fullname}' is too short"}),
                400,
            )

        db_user = VNUser.query.filter_by(
            vn_user_addr_email=addr_email,
            vn_user_phonenumber_one=phonenumber
        ).one_or_none()

        if db_user is None:
            return (
                jsonify(
                    {"message": f"This address email '{addr_email}' is taken !"}),
                int(HTTPStatus.CONFLICT),
            )

        password_hashed = generate_password_hash(password)

        new_user = User(
            vn_user_gender=gender,
            vn_user_fullname=fullname,
            vn_user_addr_email=addr_email,
            vn_user_cni_number=cni_number,
            vn_user_phonenumber_one=phonenumber,
            vn_user_country=country,
            vn_user_password=password
        )
        new_user.vn_user_activated = True
        new_user.vn_user_account_type = AccountType.IS_HOUSE_OWNER
        new_user.save()
        return {"user": new_user}, int(HTTPStatus.CREATED)
