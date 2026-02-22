import logging
import os
from logging.handlers import RotatingFileHandler

from celery import Celery, Task
from flask import Flask, redirect, render_template, url_for

from config import config
from src import exts


def create_venone_app(config_name):
    venone_app = Flask(__name__)
    venone_app.config.from_object(config[config_name])
    config[config_name].init_app(venone_app)

    venone_app.url_map.strict_slashes = False
    venone_app.jinja_env.globals.update(zip=zip)

    exts.oauth.init_app(venone_app)
    exts.mail.init_app(venone_app)
    exts.bcrypt.init_app(venone_app)
    exts.moment.init_app(venone_app)
    exts.pages.init_app(venone_app)
    exts.csrf.init_app(venone_app)

    exts.cache.init_app(venone_app)
    exts.login_manager.init_app(venone_app)

    exts.minify.init_app(venone_app)
    exts.db.init_app(venone_app)
    exts.migrate.init_app(venone_app, exts.db)
    exts.ma.init_app(venone_app)

    celery_init_app(venone_app)

    if venone_app.debug:
        from werkzeug.middleware.profiler import ProfilerMiddleware as prof  # noqa: F401

        exts.toolbar.init_app(venone_app)

    exts.cors.init_app(
        venone_app,
        origins=[
            "https://venone.app",
            "https://www.venone.app",
            "https://g.venone.app",
        ],
    )

    with venone_app.app_context():
        from src.api import api
        from src.auth import auth_bp
        from src.dashboard.routes import (admin_bp, agency_bp, checkout_bp,
                                          owner_bp)

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
    celery_app = Celery(
        app.name,
        broker_url=os.getenv("CELERY_BROKER_URL"),
        result_backend=os.getenv("CELERY_BROKER_URL"),
    )
    celery_app.conf.update(app.config)

    class ContextTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = ContextTask
    return celery_app
