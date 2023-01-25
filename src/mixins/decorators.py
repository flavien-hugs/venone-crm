from functools import wraps

from flask import flash, abort
from flask_login import current_user
from src.auth.models import Permission


def permission_required(permission):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                flash("Vous n'êtes pas autorisé à accéder à cette page.", category='warning')
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(func):
    return permission_required(Permission.ADMIN)(func)
