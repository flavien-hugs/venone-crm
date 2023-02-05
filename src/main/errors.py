import os

from flask import Blueprint
from flask import current_app
from flask import jsonify
from flask import render_template
from flask import request
from flask import send_from_directory

error_bp = Blueprint("error_bp", __name__, url_prefix="/error/")


@error_bp.app_errorhandler(403)
def forbidden(e):
    if (
        request.accept_mimetypes.accept_json
        and not request.accept_mimetypes.accept_html
    ):
        response = jsonify({"error": "forbidden"})
        response.status_code = 403
        return response
    return render_template("pages/error.html"), 403


@error_bp.app_errorhandler(404)
def page_not_found(e):
    if (
        request.accept_mimetypes.accept_json
        and not request.accept_mimetypes.accept_html
    ):
        response = jsonify({"error": "not found"})
        response.status_code = 404
        return response
    return render_template("pages/error.html"), 404


@error_bp.app_errorhandler(500)
def internal_server_error(e):
    if (
        request.accept_mimetypes.accept_json
        and not request.accept_mimetypes.accept_html
    ):
        response = jsonify({"error": "internal server error"})
        response.status_code = 500
        return response
    return render_template("pages/error.html"), 500


@error_bp.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, "static"),
        "img/logo/favicon.png",
        mimetype="img/logo/favicon.png",
    )
