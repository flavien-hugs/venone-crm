import os

from flask import Flask, redirect, url_for

from src.api.shared.errors import register_error_handlers
from src.infrastructure.config.celery_config import celery_init_app
from src.infrastructure.config.logging import setup_logging
from src.infrastructure.config.plugins import init_plugins
from src.infrastructure.config.settings import config
from src.infrastructure.commands.manage import register_commands
from src.infrastructure.shared.helpers import formatted_number


def create_app(config_name: str = "dev"):
    """
    Application Factory for Venone CRM.
    Optimized for SOLID: coordinates initialization without knowing implementation.
    """
    app = Flask(__name__)

    # Configuration
    conf_obj = config.get(config_name, config["dev"])
    app.config.from_object(conf_obj)
    conf_obj.init_app(app)

    # Infrastructure plugins
    init_plugins(app)

    # Logging
    setup_logging(app)

    # Flask engine tweaks
    app.url_map.strict_slashes = False
    app.jinja_env.globals.update(zip=zip)
    app.jinja_env.filters["format_amount"] = formatted_number

    with app.app_context():
        # Blueprint and interface registration
        register_blueprints(app)
        register_error_handlers(app)
        setup_upload_dirs(app)

        # Celery background support
        celery_init_app(app)

        # Register custom CLI commands
        register_commands(app)

    @app.route("/")
    def entrypoint():
        return redirect(url_for("auth_bp.login"))

    return app


def register_blueprints(app):
    """Encapsulation of all blueprints registration."""
    from src.api import api_bp, auth
    from src.dashboard.routes import admin_bp, agency_bp, checkout_bp, owner_bp

    from src.infrastructure.config.plugins import csrf

    csrf.exempt(api_bp)
    csrf.exempt(checkout_bp)

    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(owner_bp)
    app.register_blueprint(agency_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)


def setup_upload_dirs(app):
    """Ensures necessary file upload directories exist."""
    upload_path = app.config.get("UPLOAD_FOLDER_PATH", "upload")
    if not os.path.exists(upload_path):
        try:
            os.makedirs(upload_path, exist_ok=True)
        except OSError:
            app.logger.warning(f"Failed to create upload dir: {upload_path}")
