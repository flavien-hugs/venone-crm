import os

from flask import Blueprint
from flask import current_app
from flask import make_response
from flask import render_template
from flask import send_from_directory
from flask import url_for
from flask_wtf.csrf import CSRFError

error_bp = Blueprint("error_bp", __name__)


@error_bp.errorhandler(CSRFError)
def handle_csrf_error(e):
    page_title = e.name
    image_path = url_for("static", filename="img/error/404.svg")
    return (
        render_template(
            "pages/error.html", page_title=page_title, image_path=image_path, error=e
        ),
        400,
    )


@error_bp.errorhandler(400)
def key_error(e):
    page_title = e.name
    current_app.logger.warning(page_title, exc_info=e)
    image_path = url_for("static", filename="img/error/404.svg")
    return make_response(
        render_template(
            "pages/error.html", page_title=page_title, image_path=image_path, error=e
        ),
        400,
    )


@error_bp.app_errorhandler(403)
def forbidden(e):
    page_title = f"erreur {e}"
    current_app.logger.warning(page_title, exc_info=e)
    image_path = url_for("static", filename="img/error/403.svg")
    return make_response(
        render_template(
            "pages/error.html", page_title=page_title, image_path=image_path, error=e
        ),
        403,
    )

@error_bp.app_errorhandler(404)
def page_not_found(e):
    page_title = e.name
    current_app.logger.warning(page_title, exc_info=e)
    image_path = url_for("static", filename="img/error/404.svg")
    return make_response(
        render_template(
            "pages/error.html", page_title=page_title, image_path=image_path, error=e
        ),
        404,
    )


@error_bp.app_errorhandler(500)
def internal_server_error(e):
    page_title = e.name
    current_app.logger.warning(page_title, exc_info=e)
    image_path = url_for("static", filename="img/error/500.svg")
    return make_response(
        render_template(
            "pages/error.html", page_title=page_title, image_path=image_path, error=e
        ),
        500,
    )


@error_bp.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, "static"),
        "img/logo/favicon.png",
        mimetype="img/logo/favicon.png",
    )
