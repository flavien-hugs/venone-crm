import logging
import os
from logging.handlers import RotatingFileHandler

from config import config
from flask import current_app
from flask import Flask
from flask import redirect
from flask import render_template
from flask import send_from_directory
from flask import url_for
from flask_apscheduler import APScheduler
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_cors import CORS
from flask_flatpages import FlatPages
from flask_htmlmin import HTMLMIN
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFError
from flask_wtf.csrf import CSRFProtect

cors = CORS()
mail = Mail()
bcrypt = Bcrypt()
db = SQLAlchemy()
moment = Moment()
migrate = Migrate()
pages = FlatPages()
csrf = CSRFProtect()
scheduler = APScheduler()
login_manager = LoginManager()
cache = Cache(config={"CACHE_TYPE": "simple"})
htmlmin = HTMLMIN(remove_comments=False, remove_empty_space=True)

login_manager.login_view = "auth_bp.login"
login_manager.session_protection = "strong"
login_manager.login_message_category = "info"
login_manager.needs_refresh_message_category = "danger"


def create_venone_app(config_name):
    venone_app = Flask(__name__)
    venone_app.config.from_object(config[config_name])
    config[config_name].init_app(venone_app)

    venone_app.url_map.strict_slashes = False
    venone_app.jinja_env.globals.update(zip=zip)

    mail.init_app(venone_app)
    bcrypt.init_app(venone_app)
    moment.init_app(venone_app)
    pages.init_app(venone_app)
    htmlmin.init_app(venone_app)
    csrf.init_app(venone_app)

    cache.init_app(venone_app)
    scheduler.init_app(venone_app)
    login_manager.init_app(venone_app)

    migrate.init_app(venone_app, db)
    db.init_app(venone_app)

    with venone_app.app_context():

        from src.auth import auth_bp
        from src.dashboard.routes import owner_bp, agency_bp, admin_bp

        venone_app.register_blueprint(auth_bp)
        venone_app.register_blueprint(owner_bp)
        venone_app.register_blueprint(agency_bp)
        venone_app.register_blueprint(admin_bp)

        @venone_app.errorhandler(CSRFError)
        def handle_csrf_error(e):
            page_title = e.name
            image_path = url_for("static", filename="img/error/404.svg")
            return (
                render_template(
                    "pages/error.html",
                    page_title=page_title,
                    image_path=image_path,
                    error=e,
                ),
                400,
            )

        @venone_app.errorhandler(400)
        def key_error(e):
            page_title = e.name
            current_app.logger.warning(page_title, exc_info=e)
            image_path = url_for("static", filename="img/error/404.svg")
            return (
                render_template(
                    "pages/error.html",
                    page_title=page_title,
                    image_path=image_path,
                    error=e,
                ),
                400,
            )

        @venone_app.errorhandler(403)
        def forbidden(e):
            page_title = f"erreur {e}"
            current_app.logger.warning(page_title, exc_info=e)
            image_path = url_for("static", filename="img/error/403.svg")
            return (
                render_template(
                    "pages/error.html",
                    page_title=page_title,
                    image_path=image_path,
                    error=e,
                ),
                403,
            )

        @venone_app.errorhandler(404)
        def page_not_found(e):
            page_title = e.name
            current_app.logger.warning(page_title, exc_info=e)
            image_path = url_for("static", filename="img/error/404.svg")
            return (
                render_template(
                    "pages/error.html",
                    page_title=page_title,
                    image_path=image_path,
                    error=e,
                ),
                404,
            )

        @venone_app.errorhandler(500)
        def internal_server_error(e):
            page_title = e.name
            current_app.logger.warning(page_title, exc_info=e)
            image_path = url_for("static", filename="img/error/500.svg")
            return (
                render_template(
                    "pages/error.html",
                    page_title=page_title,
                    image_path=image_path,
                    error=e,
                ),
                500,
            )

        @venone_app.route("/favicon.ico")
        def favicon():
            return send_from_directory(
                os.path.join(current_app.root_path, "static"),
                "img/logo/favicon.png",
                mimetype="img/logo/favicon.png",
            )

        try:
            if not os.path.exists("upload"):
                os.mkdir("upload")
        except OSError:
            pass

        @venone_app.route("/")
        def entrypoint():
            return redirect(url_for("auth_bp.login"))

        if not venone_app.debug:
            if not os.path.exists("logs"):
                os.mkdir("logs")
            file_handler = RotatingFileHandler(
                "logs/logging.log", maxBytes=10240, backupCount=10
            )
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
                )
            )
            file_handler.setLevel(logging.INFO)

            venone_app.logger.addHandler(file_handler)
            venone_app.logger.setLevel(logging.INFO)
            venone_app.logger.info("running venone app")

        @venone_app.before_request
        def log_entry():
            venone_app.logger.debug("Demande de traitement")

        @venone_app.teardown_request
        def log_exit(exc):
            venone_app.logger.debug("Traitement de la demande terminé", exc_info=exc)

        return venone_app
