from src.constants import GENDER
from wtforms import SelectField
from wtforms import StringField


class DefaultForm:

    gender = SelectField(label="Genre", choices=GENDER, coerce=str)
    phonenumber_two = StringField(label="Numéro de téléphone 2")
