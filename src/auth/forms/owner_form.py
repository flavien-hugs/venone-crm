from flask_wtf import FlaskForm
from wtforms.validators import ValidationError
from wtforms import SelectField, SubmitField

from ..models import VNUser
from .form import FormMixin
from ..constants import GENDER, COUNTRY

class OwnerHouseSignupForm(FormMixin, FlaskForm):

    gender = SelectField("Genre", choices=GENDER, coerce=str)
    submit = SubmitField("Créer votre compte")

    def validate_vn_user_addr_email(self, field):
        user = VNUser.query.filter_by(vn_user_addr_email=field.data.lower()).one_or_none()
        if user:
            raise ValidationError(
                f"""
                Cet email '{field.data.lower()}' est déjà utilisé.
                Veuillez choisir un autre nom !
                """
            )

    def validate_vn_user_phonenumber_one(self, field):
        if VNUser.query.filter_by(vn_user_phonenumber_one=field.data).one_or_none():
            raise ValidationError("Ce numéro est déjà utilisé.")
