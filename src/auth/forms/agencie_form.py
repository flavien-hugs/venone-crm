from flask_wtf import FlaskForm
from src import db
from src.auth.forms.default_form import FormMixin
from src.auth.models import VNUser
from src.constants import GENDER
from wtforms import SelectField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import InputRequired
from wtforms.validators import ValidationError


class AgencieSignupForm(FormMixin, FlaskForm):

    gender = SelectField("Genre", choices=GENDER, coerce=str)
    fullname = StringField(
        "Nom du gestionnaire", validators=[DataRequired(), InputRequired()]
    )
    business_number = StringField(
        "N° de votre régistre de commerce", validators=[DataRequired(), InputRequired()]
    )
    agencie_name = StringField(
        "Nom de l'entreprise", validators=[DataRequired(), InputRequired()]
    )
    submit = SubmitField("Ouvrir mon compte")

    def validate_business_number(self, field):
        if VNUser.query.filter_by(vn_business_number=field.data).first():
            raise ValidationError(
                "Ce numéro de régistre de commerce est déjà utilisé !"
            )
