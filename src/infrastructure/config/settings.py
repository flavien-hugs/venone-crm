import os
import secrets
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def get_env_bool(name, default=False):
    """Helper to get boolean from environment variables."""
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in ("true", "1", "yes", "on")


class Config:
    """Base configuration class with environment-driven values."""

    # Flask Core
    FLASK_CONFIG = os.environ.get("FLASK_CONFIG", "dev")
    SITE_NAME = os.environ.get("SITE_NAME", "IMMO CRM")
    ADMIN_ROLE_NAME = os.environ.get("ADMIN_ROLE_NAME", "Administrateur")
    SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(64))
    PREFERRED_URL_SCHEME = os.environ.get("PREFERRED_URL_SCHEME", "http")
    SESSION_COOKIE_SECURE = get_env_bool("SESSION_COOKIE_SECURE", True)
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = get_env_bool(
        "SQLALCHEMY_TRACK_MODIFICATIONS", False
    )
    SQLALCHEMY_RECORD_QUERIES = get_env_bool("SQLALCHEMY_RECORD_QUERIES", True)
    SQLALCHEMY_ECHO = get_env_bool("SQLALCHEMY_ECHO", False)

    # Security & CSRF
    WTF_CSRF_ENABLED = get_env_bool("WTF_CSRF_ENABLED", True)

    # Mail Config
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = get_env_bool("MAIL_USE_TLS", True)
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get(
        "MAIL_DEFAULT_SENDER", os.environ.get("MAIL_SENDER")
    )
    MAIL_TIMEOUT = int(os.environ.get("MAIL_TIMEOUT", 30))
    MAIL_SUBJECT_PREFIX = os.environ.get("MAIL_SUBJECT_PREFIX", "[Support]")

    # Cache & Minify
    CACHE_TYPE = os.environ.get("CACHE_TYPE", "SimpleCache")
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", 300))
    MINIFY_HTML = get_env_bool("MINIFY_HTML", True)

    # FlatPages
    FLATPAGES_EXTENSION = os.environ.get("FLATPAGES_EXTENSION", ".md")
    FLATPAGES_AUTO_RELOAD = get_env_bool("FLATPAGES_AUTO_RELOAD", True)

    # Uploads
    UPLOAD_FOLDER_PATH = os.environ.get(
        "UPLOAD_FOLDER_PATH", os.path.join(BASE_DIR, "upload/")
    )
    ALLOWED_EXTENSIONS = os.environ.get("ALLOWED_EXTENSIONS", "png,jpg,jpeg,svg").split(
        ","
    )

    # External Services (CinetPay, SMS, Google)
    CINETPAY_SITE_ID = os.environ.get("CINETPAY_SITE_ID")
    CINETPAY_API_KEY = os.environ.get("CINETPAY_API_KEY")

    SMS_API_KEY = os.environ.get("SMS_API_KEY")
    SMS_BASE_URL = os.environ.get("SMS_BASE_URL")
    SMS_SENDER_ID = os.environ.get("SMS_SENDER_ID")
    SMS_API_TOKEN = os.environ.get("SMS_API_TOKEN")

    GOOGLE_CONF_URL = os.environ.get("GOOGLE_CONF_URL")
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_SECRET_KEY = os.environ.get("GOOGLE_SECRET_KEY")

    # Admin Seed Info
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@venone.app")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "password")
    ADMIN_PHONE_NUMBER = os.environ.get("ADMIN_PHONE_NUMBER")

    # Application Specific
    TOKEN_EXPIRATION_TIME = timedelta(
        days=int(os.environ.get("TOKEN_EXPIRATION_DAYS", 3))
    )
    ALLOWED_COUNTRIES = os.environ.get(
        "ALLOWED_COUNTRIES", "SN,TG,BF,CM,CG,GN,CD,NE,BJ,ML,KM"
    ).split(",")

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    TEMPLATES_AUTO_RELOAD = get_env_bool("TEMPLATES_AUTO_RELOAD", True)
    DEBUG_TB_INTERCEPT_REDIRECTS = get_env_bool("DEBUG_TB_INTERCEPT_REDIRECTS", False)


class TestingConfig(Config):
    pass


class ProductionConfig(Config):
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        import logging
        from logging.handlers import SysLogHandler

        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


config = {
    "prod": ProductionConfig,
    "dev": DevelopmentConfig,
    "test": TestingConfig,
}
