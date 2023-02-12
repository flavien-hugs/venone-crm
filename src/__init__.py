import logging
import os
from logging.handlers import RotatingFileHandler

from config import config
from flask import Flask
from flask import redirect
from flask import url_for
from flask_apscheduler import APScheduler
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_session import Session
from flask_cors import CORS
from flask_flatpages import FlatPages
from flask_htmlmin import HTMLMIN
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
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
session = Session()
login_manager = LoginManager()
cache = Cache(config={"CACHE_TYPE": "simple"})
htmlmin = HTMLMIN(remove_comments=False, remove_empty_space=True)

login_manager.login_view = "auth_bp.login"
login_manager.session_protection = "strong"
login_manager.login_message_category = "info"


def create_venone_app(config_name):
    venone_app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
        instance_relative_config=True,
    )
    venone_app.config.from_object(config[config_name])
    config[config_name].init_app(venone_app)

    venone_app.url_map.strict_slashes = False
    venone_app.jinja_env.globals.update(zip=zip)

    cache.init_app(venone_app)
    mail.init_app(venone_app)
    bcrypt.init_app(venone_app)
    moment.init_app(venone_app)
    pages.init_app(venone_app)
    htmlmin.init_app(venone_app)
    migrate.init_app(venone_app, db)
    db.init_app(venone_app)
    csrf.init_app(venone_app)
    session.init_app(venone_app)
    
    scheduler.init_app(venone_app)
    login_manager.init_app(venone_app)

    with venone_app.app_context():

        from src.auth import auth_bp
        from src.main import error_bp
        from src.dashboard.routes import owner_bp, agency_bp, admin_bp

        venone_app.register_blueprint(auth_bp)
        venone_app.register_blueprint(owner_bp)
        venone_app.register_blueprint(agency_bp)
        venone_app.register_blueprint(admin_bp)
        venone_app.register_blueprint(error_bp)

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
