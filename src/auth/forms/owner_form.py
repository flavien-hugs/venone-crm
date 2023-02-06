from flask_wtf import FlaskForm
from src.auth.forms.default_form import FormMixin
from src.constants import GENDER
from wtforms import SelectField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import InputRequired


class OwnerHouseSignupForm(FormMixin, FlaskForm):

    gender = SelectField("Genre", choices=GENDER, coerce=str)
    fullname = StringField(
        "Nom et prénom", validators=[DataRequired(), InputRequired()]
    )
    cni_number = StringField(
        "N° de votre CNI", validators=[DataRequired(), InputRequired()]
    )
    submit = SubmitField("Ouvrir mon compte")
