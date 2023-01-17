import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, request, make_response

from flask_restx import Api
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

from config import config

db = SQLAlchemy()
cors = CORS()
migrate = Migrate()
jwt = JWTManager()

authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}
api = Api(
    version="1.0",
    title="Venone API",
    description="A Venone API",
    authorizations=authorizations,
)


def output_xml(data, code, headers=None):
    """Makes a Flask response with a XML encoded body"""
    resp = make_response(dumps({"response": data}), code)
    resp.headers.extend(headers or {})
    return resp


api.representations["application/xml"] = output_xml


def create_venone_app(config_name):
    venone_app = Flask(__name__, instance_relative_config=True)
    venone_app.config.from_object(config[config_name])
    config[config_name].init_app(venone_app)

    cors.init_app(venone_app)
    jwt.init_app(venone_app)
    api.init_app(venone_app)
    migrate.init_app(venone_app, db)
    db.init_app(venone_app)

    with venone_app.app_context():

        from .auth import auth  # noqa

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

        @venone_app.after_request
        def after_request(response):
            request.get_data()
            return response

        return venone_app
