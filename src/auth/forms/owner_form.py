from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import InputRequired

from ..constants import GENDER
from .form import FormMixin


class OwnerHouseSignupForm(FormMixin, FlaskForm):

    gender = SelectField("Genre", choices=GENDER, coerce=str)
    fullname = StringField(
        "Nom et prénom", validators=[DataRequired(), InputRequired()]
    )
    cni_number = StringField(
        "N° de votre CNI", validators=[DataRequired(), InputRequired()]
    )
    submit = SubmitField("Créer votre compte")
