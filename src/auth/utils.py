import logging
import os
import secrets
from datetime import datetime
from datetime import timedelta

import jwt
from flask import current_app
from flask import request
from werkzeug.utils import secure_filename

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


def upload_avatar(picture):
    picture = request.files["picture"]
    if picture and allowed_file(picture.filename):
        filename = secure_filename(picture.filename)
        _, extension = os.path.splitext(filename)
        random_hex = secrets.token_hex(8)
        picture_fn = random_hex + extension

        if picture_fn:
            file_path = os.path.join(
                current_app.config["UPLOAD_FOLDER_PATH"], picture_fn
            )
            if os.path.exists(file_path):
                os.remove(file_path)
            logger.debug(f"file {file_path} does not exist!")
        picture.save(os.path.join(current_app.config["UPLOAD_FOLDER_PATH"], picture_fn))
        return picture_fn


def generate_confirm_token(email):
    payload = {
        "email": email,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1),
    }

    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    return token


def confirm_token(token):
    try:
        payload = jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
        )
        return payload["email"]
    except jwt.exceptions.ExpiredSignatureError as e:
        logger.debug(e)
        raise jwt.BadRequest(
            "Le lien de réinitialisation de mot de passe est invalide ou expiré."
        ) from e
    except jwt.exceptions.InvalidTokenError as e:
        logger.debug(e)
        raise jwt.BadRequest("Token invalide.") from e
