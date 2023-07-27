import os
from datetime import timedelta
from typing import Generator

from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

env = dotenv_values(".flaskenv")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE_URI = env.get("DATABASE_URL") or "sqlite:///" + os.path.join(
    BASE_DIR, "dev.sqlite3"
)
engine = create_engine(DATABASE_URI, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = scoped_session(SessionLocal)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Config:
    DEBUG = False
    TESTING = False
    DEVELOPMENT = False

    SITE_NAME = "Venone"

    SERVER_NAME = "127.0.0.1:5000"
    PREFERRED_URL_SCHEME = "http"
    SESSION_COOKIE_SECURE = True

    SECRET_KEY = env.get("SECRET_KEY", os.urandom(24))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ECHO = False

    MAIL_TIMEOUT = 30
    MAIL_SUBJECT_PREFIX = "[Venone]"
    MAIL_PORT = env.get("MAIL_PORT")
    MAIL_SERVER = env.get("MAIL_SERVER")
    MAIL_USE_TLS = env.get("MAIL_USE_TLS")
    MAIL_USERNAME = env.get("MAIL_USERNAME")
    MAIL_SENDER = "Venone <noreply@venone.app>"
    MAIL_PASSWORD = env.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = MAIL_SENDER

    FLATPAGES_EXTENSION = ".md"
    FLATPAGES_MARKDOWN_EXTENSIONS = ["codehilite"]

    MAX_CONTENT_LENGTH = 16 * 1000 * 1000
    ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "svg"]
    UPLOAD_FOLDER_PATH = os.path.join(BASE_DIR, "upload/")

    MINIFY_HTML = True

    WEBSITE_BUILDER = "gestion.venone.app"
    WTF_CSRF_ENABLED = False

    CINETPAY_SITE_ID = env.get("CINETPAY_SITEID")
    CINETPAY_API_KEY = env.get("CINETPAY_APIKEY")

    SMS_API_KEY = env.get("SMS_APIKEY")
    SMS_BASE_URL = env.get("SMS_BASEURL")
    SMS_SENDER_ID = env.get("SMS_SENDERID")
    SMS_API_TOKEN = env.get("SMS_APITOKEN")

    ADMIN_PHONE_NUMBER = env.get("ADMIN_PHONE_NUMBER")
    ADMIN_PASSWORD = env.get("ADMIN_PASSWORD")
    ADMIN_EMAIL = env.get("ADMIN_EMAIL")
    ADMIN_USERNAME = env.get("ADMIN_USERNAME")

    TOKEN_EXPIRATION_TIME = timedelta(days=3)

    GOOGLE_CONF_URL = env.get("GG_CONF_URL")
    GOOGLE_CLIEND_ID = env.get("GG_CLIEND_ID")
    GOOGLE_SECRET_KEY = env.get("GG_SECRET_KEY")

    ALLOWED_COUNTRIES = [
        "SN",
        "TG",
        "BF",
        "CM",
        "CG",
        "GN",
        "CD",
        "NE",
        "BJ",
        "ML",
        "KM",
    ]

    @staticmethod
    def init_app(venone_app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    TEMPLATES_AUTO_RELOAD = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_DATABASE_URI = DATABASE_URI


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    DATABASE_URI = env.get("DATABASE_URL")
    SQLALCHEMY_DATABASE_URI = DATABASE_URI

    @classmethod
    def init_app(cls, venone_app):
        Config.init_app(venone_app)
        import logging
        from logging.handlers import SysLogHandler

        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        venone_app.logger.addHandler(syslog_handler)


config = {
    "prod": ProductionConfig,
    "dev": DevelopmentConfig,
    "test": TestingConfig,
}
