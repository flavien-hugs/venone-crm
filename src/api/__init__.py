from flask import Blueprint

api = Blueprint("api", __name__, url_prefix="/api/")

from . import chart, checkout, house, owner, tenant, user  # noqa

__all__ = (
    "user",
    "tenant",
    "owner",
    "house",
    "checkout",
    "chart",
)
