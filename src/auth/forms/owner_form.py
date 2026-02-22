from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, InputRequired

from src.auth.forms.default_form import FormMixin
from src.constants import GENDER


class OwnerHouseSignupForm(FormMixin, FlaskForm):
    gender = SelectField("Genre", choices=GENDER, coerce=str)
    fullname = StringField(
        "Nom et prénom",
        validators=[DataRequired(), InputRequired()],
        render_kw={"required": True},
    )
    cni_number = StringField(
        "N° de votre CNI",
        validators=[DataRequired(), InputRequired()],
        render_kw={"required": True},
    )
    submit = SubmitField("Ouvrir mon compte")
