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
from authlib.integrations.flask_client import OAuth

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

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
cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 300})

minify = Minify(html=True, js=True, cssless=True, bypass=["owner_bp.*", "agency_bp.*"])
toolbar = DebugToolbarExtension()

login_manager.login_view = "auth_bp.login"
login_manager.session_protection = "strong"
login_manager.login_message_category = "info"
login_manager.needs_refresh_message_category = "info"
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
login_manager.needs_refresh_message = "Pour protéger votre compte,\
    veuillez vous réauthentifier pour accéder à cette page."
