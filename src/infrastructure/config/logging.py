import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(app):
    """Setup file logging for Production or non-debug modes."""
    if not app.debug:
        log_dir = os.environ.get("LOG_DIR", "logs")
        if not os.path.exists(log_dir):
            try:
                os.mkdir(log_dir)
            except OSError:
                app.logger.warning("Could not create logging directory.")

        file_handler = RotatingFileHandler(
            os.path.join(log_dir, "logging.log"), maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)

        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("Venone CRM application starting...")
