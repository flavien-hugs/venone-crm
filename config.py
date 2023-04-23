"""
Global Flask Application Setting
See `.flaskenv` for default settings.
"""
import os
from datetime import timedelta
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

dotenv_path = os.path.join(os.path.dirname(__file__), ".flaskenv")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///" + os.path.join(
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

    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(24))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ECHO = False

    MAIL_TIMEOUT = 30
    MAIL_SUBJECT_PREFIX = "[Venone]"
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_SENDER = "Venone <noreply@venone.app>"
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = MAIL_SENDER

    FLATPAGES_EXTENSION = ".md"
    FLATPAGES_MARKDOWN_EXTENSIONS = ["codehilite"]

    MAX_CONTENT_LENGTH = 16 * 1000 * 1000
    ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "svg"]
    UPLOAD_FOLDER_PATH = os.path.join(BASE_DIR, "upload/")

    MINIFY_HTML = True

    WEBSITE_BUILDER = "gestion.venone.app"
    WTF_CSRF_ENABLED = False

    CINETPAY_SITE_ID = os.getenv("CINETPAY_SITEID")
    CINETPAY_API_KEY = os.getenv("CINETPAY_APIKEY")

    SMS_API_KEY = os.getenv("SMS_APIKEY")
    SMS_BASE_URL = os.getenv("SMS_BASEURL")
    SMS_SENDER_ID = os.getenv("SMS_SENDERID")
    SMS_API_TOKEN = os.getenv("SMS_APITOKEN")

    ADMIN_PHONE_NUMBER = os.getenv("ADMIN_PHONE_NUMBER")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")

    TOKEN_EXPIRATION_TIME = timedelta(days=3)

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

    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_DATABASE_URI = DATABASE_URI


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):

    DATABASE_URI = os.getenv("DATABASE_URL")
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
