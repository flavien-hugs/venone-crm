import os
import secrets
from datetime import timedelta
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(
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

    SITE_NAME = os.environ.get("SITE_NAME", "IMMO CRM")
    ADMIN_ROLE_NAME = os.environ.get("ADMIN_ROLE_NAME", "Administrateur")
    PREFERRED_URL_SCHEME = "http"
    SESSION_COOKIE_SECURE = True

    # SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(64))
    SECRET_KEY = secrets.token_hex(64)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ECHO = False

    MAIL_TIMEOUT = 30
    MAIL_SUBJECT_PREFIX = "[Venone]"
    MAIL_PORT = os.environ.get("MAIL_PORT")
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_SENDER = os.environ.get("MAIL_SENDER")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = MAIL_SENDER

    FLATPAGES_EXTENSION = ".md"
    FLATPAGES_MARKDOWN_EXTENSIONS = ["codehilite"]

    MAX_CONTENT_LENGTH = 16 * 1000 * 1000
    ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "svg"]
    UPLOAD_FOLDER_PATH = os.path.join(BASE_DIR, "upload/")

    MINIFY_HTML = True

    WEBSITE_BUILDER = os.environ.get("WEBSITE_BUILDER")
    WTF_CSRF_ENABLED = False

    CINETPAY_SITE_ID = os.environ.get("CINETPAY_SITEID")
    CINETPAY_API_KEY = os.environ.get("CINETPAY_APIKEY")

    SMS_API_KEY = os.environ.get("SMS_API_KEY")
    SMS_BASE_URL = os.environ.get("SMS_BASE_URL")
    SMS_SENDER_ID = os.environ.get("SMS_SENDER_ID")
    SMS_API_TOKEN = os.environ.get("SMS_API_TOKEN")

    ADMIN_PHONE_NUMBER = os.environ.get("ADMIN_PHONE_NUMBER")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")

    TOKEN_EXPIRATION_TIME = timedelta(days=3)

    GOOGLE_CONF_URL = os.environ.get("GG_CONF_URL")
    GOOGLE_CLIEND_ID = os.environ.get("GG_CLIEND_ID")
    GOOGLE_SECRET_KEY = os.environ.get("GG_SECRET_KEY")

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
    TEMPLATES_AUTO_RELOAD = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_DATABASE_URI = DATABASE_URI


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SERVER_NAME = "localhost.localdomain"


class ProductionConfig(Config):
    DATABASE_URI = os.environ.get("DATABASE_URL")
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
