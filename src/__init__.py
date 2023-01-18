import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, request, make_response

from flask_cors import CORS
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_moment import Moment
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_flatpages import FlatPages
from flask_sqlalchemy import SQLAlchemy

from config import config

cors = CORS()
mail = Mail()
bcrypt = Bcrypt()
db = SQLAlchemy()
moment = Moment()
migrate = Migrate()
pages = FlatPages()
login_manager = LoginManager()

login_manager.login_view = "admin.loginPage"
login_manager.session_protection = "strong"
login_manager.login_message_category = "info"
login_manager.needs_refresh_message_category = "danger"


def create_venone_app(config_name):
    venone_app = Flask(__name__, instance_relative_config=True)
    venone_app.config.from_object(config[config_name])
    config[config_name].init_app(venone_app)

    mail.init_app(venone_app)
    bcrypt.init_app(venone_app)
    moment.init_app(venone_app)
    pages.init_app(venone_app)
    cors.init_app(venone_app)
    login_manager.init_app(venone_app)

    migrate.init_app(venone_app, db)
    db.init_app(venone_app)

    with venone_app.app_context():

        from .auth.routes import auth_view
        venone_app.register_blueprint(auth_view)

        try:
            if not os.path.exists("upload"):
                os.mkdir("upload")
        except OSError:
            pass

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

        @venone_app.after_request
        def after_request(response):
            request.get_data()
            return response

        return venone_app
