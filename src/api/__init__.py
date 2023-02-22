from flask import Blueprint

api = Blueprint("api", __name__, url_prefix="/api/")

from . import tenant, owner, house  # noqa

__all__ = (
    "tenant",
    "owner",
    "house",
)
