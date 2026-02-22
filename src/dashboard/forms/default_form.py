from wtforms import SelectField, StringField
from wtforms.validators import InputRequired, Optional

from src.constants import DEVISE, DEVISE_DEFAULT, GENDER, GENDER_DEFAULT


class DefaultForm:
    gender = SelectField(
        label="Genre",
        choices=GENDER,
        coerce=str,
        default=GENDER_DEFAULT,
        validators=[Optional()],
    )
    phonenumber_two = StringField(
        label="Numéro de téléphone 2", validators=[Optional()]
    )
    devise = SelectField(
        label="Devise",
        render_kw={"required": True},
        validators=[InputRequired()],
        choices=DEVISE,
        coerce=str,
        default=DEVISE_DEFAULT,
    )
