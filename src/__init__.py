import logging
import os
from logging.handlers import RotatingFileHandler

from celery import Celery
from celery import Task
from config import config
from flask import Flask
from flask import redirect
from flask import render_template
from flask import url_for
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension
from flask_flatpages import FlatPages
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_minify import Minify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import MetaData

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

cors = CORS()
mail = Mail()
bcrypt = Bcrypt()
db = SQLAlchemy(metadata=metadata)
moment = Moment()
migrate = Migrate()
pages = FlatPages()
csrf = CSRFProtect()
login_manager = LoginManager()
cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 300})

minify = Minify(html=True, js=True, cssless=True, bypass=["owner_bp.*", "agency_bp.*"])
toolbar = DebugToolbarExtension()

login_manager.login_view = "auth_bp.login"
login_manager.session_protection = "strong"
login_manager.login_message_category = "info"
login_manager.needs_refresh_message_category = "info"
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
login_manager.needs_refresh_message = "Pour protéger votre compte,\
    veuillez vous réauthentifier pour accéder à cette page."


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
    csrf.init_app(venone_app)

    cache.init_app(venone_app)
    login_manager.init_app(venone_app)

    minify.init_app(venone_app)
    toolbar.init_app(venone_app)

    db.init_app(venone_app)
    migrate.init_app(venone_app, db)

    celery_init_app(venone_app)

    with venone_app.app_context():

        from src.auth import auth_bp
        from src.dashboard.routes import owner_bp, agency_bp, admin_bp, checkout_bp
        from src.api import api

        venone_app.register_blueprint(auth_bp)
        venone_app.register_blueprint(owner_bp)
        venone_app.register_blueprint(agency_bp)
        venone_app.register_blueprint(checkout_bp)
        venone_app.register_blueprint(admin_bp)

        venone_app.register_blueprint(api)

        @venone_app.errorhandler(400)
        def key_error(e):
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

        @venone_app.errorhandler(403)
        def forbidden(e):
            page_title = f"erreur {e}"
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

        return venone_app


def celery_init_app(app):
    celery_app = Celery(app.name, backend=os.getenv("CELERY_BROKER_URL"))
    celery_app.conf.update(app.config)

    class ContextTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = ContextTask
    return celery_app
