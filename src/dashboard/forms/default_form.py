from wtforms import SelectField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import Email
from wtforms.validators import DataRequired
from wtforms.validators import InputRequired

from src.auth.constants import COUNTRY, GENDER


class DefaultForm:

    gender = SelectField("Genre", choices=GENDER, coerce=str)
    phonenumber_two = StringField("Numéro de téléphone 2", validators=[InputRequired()])
