from functools import wraps

from flask import abort
from flask import flash
from flask import render_template
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


def check_activated(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.vn_user_activated is False:
            flash('Désolé, votre compte a été désactivé !', category='warning')
            return redirect(url_for('auth_bp.unactivated'))
        return func(*args, **kwargs)

    return decorated_function


def owner_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.vn_user_house_owner:
            return func(*args, **kwargs)
        return render_template("pages/no_access.html", page_title="Accès non autorisé")
    return decorated_function


def agency_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.vn_user_company:
            return func(*args, **kwargs)
        return render_template("pages/no_access.html", page_title="Accès non autorisé")
    return decorated_function
