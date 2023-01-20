from flask import Blueprint

auth_view = Blueprint("auth_view", __name__, url_prefix="/auth/customer/")

from . import auth  # noqa
from . import owner  # noqa
