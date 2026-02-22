from functools import wraps

from flask import abort, flash
from flask_login import current_user

from src.auth.models import Permission


def permission_required(permission):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                flash(
                    "Vous n'êtes pas autorisé à accéder à cette page.",
                    category="warning",
                )
                abort(403)
            return func(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(func):
    return permission_required(Permission.ADMIN)(func)


def owner_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.vn_company and current_user.vn_activated:
            abort(403)
        return func(*args, **kwargs)

    return decorated_function


def agency_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.vn_house_owner and current_user.vn_activated:
            abort(403)
        return func(*args, **kwargs)

    return decorated_function
