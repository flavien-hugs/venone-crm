from flask import Blueprint

auth_view = Blueprint("auth_view", __name__, url_prefix="/auth/")
owner_view = Blueprint("owner_view", __name__, url_prefix="/dashboard/owner/")

from . import auth  # noqa
from .dashboard import owner  # noqa
