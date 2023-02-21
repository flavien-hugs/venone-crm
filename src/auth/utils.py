import os
import secrets
from flask import current_app, request
from werkzeug.utils import secure_filename


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
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER_PATH"], picture_fn)
            if os.path.exists(file_path):
                os.remove(file_path)
            print(f'file {file_path} does not exist!')
        picture.save(os.path.join(current_app.config["UPLOAD_FOLDER_PATH"], picture_fn))
        return picture_fn
