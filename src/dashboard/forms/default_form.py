from src.auth.constants import GENDER
from wtforms import SelectField
from wtforms import StringField


class DefaultForm:

    gender = SelectField("Genre", choices=GENDER, coerce=str)
    phonenumber_two = StringField("Numéro de téléphone 2")
