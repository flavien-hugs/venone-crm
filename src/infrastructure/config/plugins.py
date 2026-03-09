from typing import TYPE_CHECKING

from authlib.integrations.flask_client import OAuth
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension
from flask_flatpages import FlatPages
from flask_login import LoginManager
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_minify import Minify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import MetaData

if TYPE_CHECKING:
    from flask import Flask

# Naming convention for database constraints to ensure migrations work smoothly
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

# Plugin instances
cors = CORS()
mail = Mail()
oauth = OAuth()
bcrypt = Bcrypt()
ma = Marshmallow()
db = SQLAlchemy(metadata=metadata)
moment = Moment()
migrate = Migrate(render_as_batch=True)
pages = FlatPages()
csrf = CSRFProtect()
login_manager = LoginManager()
cache = Cache()  # Configuration is handled in init_app
minify = Minify()  # Configuration is handled in init_app
toolbar = DebugToolbarExtension()


def init_plugins(app: "Flask") -> None:
    """
    Initialize all Flask plugins with the application instance.
    This follows the Factory Pattern, keeping the production logic clean.
    """
    oauth.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    moment.init_app(app)
    pages.init_app(app)
    csrf.init_app(app)

    # Cache config taken from app.config (defined in settings.py)
    cache.init_app(app)

    # Login Manager configuration
    login_manager.login_view = "auth_bp.login"
    login_manager.session_protection = "strong"
    login_manager.login_message_category = "info"
    login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
    login_manager.init_app(app)

    # Minify with bypass rules from config if needed
    minify.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    if app.debug:
        toolbar.init_app(app)

    # CORS configuration
    cors.init_app(app, origins=["*"])
