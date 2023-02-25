"""
Global Flask Application Setting
See `.flaskenv` for default settings.
 """
import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

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
    DEVELOPMENT = False

    SITE_NAME = "Venone"

    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(24))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ECHO = False

    # mail settings
    MAIL_SUBJECT_PREFIX = "[Venone]"
    MAIL_PORT = os.environ.get("MAIL_PORT")
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_SENDER = "Venone <noreply@venone.app>"
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = MAIL_SENDER

    FLATPAGES_EXTENSION = ".md"
    FLATPAGES_MARKDOWN_EXTENSIONS = ["codehilite"]

    MAX_CONTENT_LENGTH = 16 * 1000 * 1000
    ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "svg"]
    UPLOAD_FOLDER_PATH = os.path.join(BASE_DIR, "upload/")

    MINIFY_HTML = True

    WEBSITE_BUILDER = "gestion.venone.app"

    SCHEDULER_API_ENABLED = True
    WTF_CSRF_ENABLED = False

    CINETPAY_API_KEY = os.getenv("API_KEY")
    CINETPAY_SITE_ID = os.getenv("SITE_ID")
    CINETPAY_TRANS_ID = os.getenv("TRANS_ID")

    SENDER_ID = os.getenv("SENDER_ID")
    SMS_API_KEY = os.getenv("SMS_API_KEY")

    @staticmethod
    def init_app(venone_app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True

    SQLALCHEMY_DATABASE_URI = DATABASE_URI


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
}
