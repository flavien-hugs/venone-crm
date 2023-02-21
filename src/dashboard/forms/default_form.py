from src.constants import DEVISE
from src.constants import DEVISE_DEFAULT
from src.constants import GENDER
from src.constants import GENDER_DEFAULT
from wtforms import SelectField
from wtforms import StringField


class DefaultForm:

    gender = SelectField(
        label="Genre", choices=GENDER, coerce=str, default=GENDER_DEFAULT
    )
    phonenumber_two = StringField(label="Numéro de téléphone 2")
    devise = SelectField(
        label="Devise", choices=DEVISE, coerce=str, default=DEVISE_DEFAULT
    )
