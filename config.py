"""
Global Flask Application Setting
See `.flaskenv` for default settings.
 """
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:

    DEBUG = False
    DEVELOPMENT = False

    SITE_NAME = "Venone"

    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(24))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SLOW_DB_QUERY_TIME = 0.5

    MAIL_POST = os.environ.get("MAIL_SERVER")
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_SUBJECT_PREFIX = "[Venone]"
    MAIL_SENDER = "Venone <noreply@venone.app>"
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    FLATPAGES_EXTENSION = ".md"
    FLATPAGES_MARKDOWN_EXTENSIONS = ["codehilite"]
    SLOW_DB_QUERY_TIME = 0.5

    MAX_CONTENT_LENGTH = 16 * 1000 * 1000
    ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg"]
    UPLOAD_FOLDER_PATH = os.path.join(BASE_DIR, "upload/")

    WEBSITE_BUILDER = "gestion.venone.app"

    @staticmethod
    def init_app(venone_app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(BASE_DIR, "dev.sqlite3")
    engine = create_engine(
        SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}
    )
    sessionmaker(autocommit=False, autoflush=False, bind=engine)


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(BASE_DIR, "prod.sqlite3")
    engine = create_engine(
        SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}
    )
    sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
