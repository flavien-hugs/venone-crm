from wtforms import SelectField
from wtforms import StringField

from src.constants import GENDER


class DefaultForm:

    gender = SelectField(label="Genre", choices=GENDER, coerce=str)
    phonenumber_two = StringField(label="Numéro de téléphone 2")
