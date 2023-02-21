from flask import Blueprint

api = Blueprint("api", __name__, url_prefix="/api/")

from . import tenant, owner, house

__all__ = ("tenant", "owner", "house",)
