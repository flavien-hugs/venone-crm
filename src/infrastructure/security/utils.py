import logging
import os
import secrets
from datetime import datetime, timedelta

import jwt
from flask import current_app, request
from werkzeug.utils import secure_filename

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def allowed_file(filename):
    """
    Checks if a filename has an allowed extension.
    """
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


def upload_avatar(picture):
    """
    Handles avatar image upload and saving.
    """
    picture = request.files["picture"]
    if picture and allowed_file(picture.filename):
        filename = secure_filename(picture.filename)
        _, extension = os.path.splitext(filename)
        random_hex = secrets.token_hex(8)
        picture_fn = random_hex + extension

        file_path = os.path.join(current_app.config["UPLOAD_FOLDER_PATH"], picture_fn)

        # Ensure path exists or remove old if somehow exists
        if os.path.exists(file_path):
            os.remove(file_path)

        picture.save(file_path)
        return picture_fn
    return None


def generate_confirm_token(email):
    """
    Generates a JWT token for email confirmation.
    """
    payload = {
        "email": email,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1),
    }

    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    return token


def confirm_token(token):
    """
    Decodes and validates a JWT token.
    """
    try:
        payload = jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
        )
        return payload["email"]
    except jwt.exceptions.ExpiredSignatureError as e:
        logger.debug(f"Expired token: {e}")
        raise Exception(
            "Le lien de réinitialisation de mot de passe est invalide ou expiré."
        ) from e
    except jwt.exceptions.InvalidTokenError as e:
        logger.debug(f"Invalid token: {e}")
        raise Exception("Token invalide.") from e
