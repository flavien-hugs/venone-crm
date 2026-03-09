import os

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required

from src.api.forms.auth_form import ChangePasswordForm
from src.api.middlewares import owner_required
from src.core import get_user_service
from src.dashboard.forms import OwnerSettingForm
from src.infrastructure.config.plugins import cache, csrf

owner_bp = Blueprint("owner_bp", __name__, url_prefix="/dashboard/")
csrf.exempt(owner_bp)


@owner_bp.route("/-/", methods=["GET"])
@login_required
@cache.cached(timeout=500)
def dashboard():
    page_title = "Tableau de bord"
    user_service = get_user_service()
    stats = user_service.get_dashboard_stats(current_user.id)
    owner_data = user_service.get_owner_per_month(current_user.id)
    tenant_data = user_service.get_tenant_per_month(current_user.id)
    open_houses_data = user_service.houses_opened_count(current_user.id)
    trend_price_data = user_service.get_trendprices(current_user.id)
    return render_template(
        "dashboard/dashboard.html",
        page_title=page_title,
        current_user=current_user,
        stats=stats,
        owner_data=owner_data,
        tenant_data=tenant_data,
        open_houses_data=open_houses_data,
        trend_price_data=trend_price_data,
    )


@owner_bp.route("/parameters/", methods=["GET", "POST"])
@login_required
@owner_required
def owner_setting():
    page_title = "Paramètres"
    form = OwnerSettingForm(request.form)

    if request.method == "POST" and form.validate_on_submit():
        current_user.vn_gender = form.gender.data
        current_user.vn_fullname = form.fullname.data
        current_user.vn_phonenumber_two = form.phonenumber_two.data

        current_user.vn_profession = form.profession.data
        current_user.vn_parent_name = form.parent_name.data

        current_user.vn_device = form.devise.data
        current_user.vn_location = form.location.data
        current_user.vn_birthdate = form.birthdate.data

        current_user.save()
        flash("Votre compte a été mise à jour avec succès.", "success")
        return redirect(url_for("owner_bp.owner_setting"))
    elif request.method == "GET":
        form.gender.data = current_user.vn_gender
        form.fullname.data = current_user.vn_fullname
        form.phonenumber_two.data = current_user.vn_phonenumber_two

        form.profession.data = current_user.vn_profession
        form.parent_name.data = current_user.vn_parent_name

        form.devise.data = current_user.vn_device
        form.location.data = current_user.vn_location
        form.birthdate.data = current_user.vn_birthdate

    return render_template(
        "dashboard/account/owner/settings.html",
        page_title=page_title,
        form=form,
        current_user=current_user,
    )


@owner_bp.route("/change-paswword/", methods=["GET", "POST"])
@login_required
def change_password():
    page_title = "Changer votre mot de passe"
    form = ChangePasswordForm()
    if request.method == "POST" and form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.vn_password = form.new_password.data
            current_user.set_password(form.new_password.data)
            current_user.save()
            flash("Votre mot de passe a été mise à jour avec succès.", "success")
            return redirect(url_for("owner_bp.change_password"))
        else:
            flash("Le mot de passe est invalide.", category="danger")

    return render_template(
        "dashboard/account/password.html",
        page_title=page_title,
        form=form,
        current_user=current_user,
    )


@owner_bp.route("/<filename>/")
@cache.cached(timeout=500)
def avatar(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER_PATH"], filename)


@owner_bp.route("/favicon.png")
@cache.cached(timeout=500)
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, "static"), "img/logo/favicon.png"
    )
