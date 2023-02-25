from flask import Blueprint

api = Blueprint("api", __name__, url_prefix="/api/")

from . import user, tenant, owner, house  # noqa

__all__ = (
    "user",
    "tenant",
    "owner",
    "house",
)
