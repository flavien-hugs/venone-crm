from wtforms import SelectField
from wtforms import StringField

from src.constants import GENDER


class DefaultForm:

    gender = SelectField("Genre", choices=GENDER, coerce=str)
    phonenumber_two = StringField("Numéro de téléphone 2")
