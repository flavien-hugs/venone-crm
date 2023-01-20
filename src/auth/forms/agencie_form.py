from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, InputRequired, ValidationError

from ..models import VNUser
from .form import FormMixin
from ..constants import GENDER, COUNTRY


class AgencieSignupForm(FormMixin, FlaskForm):

    gender = SelectField("Genre", choices=GENDER, coerce=str)
    fullname = StringField("Nom du gestionnaire", validators=[DataRequired(), InputRequired()])
    business_number = StringField("N° de votre régistre de commerce", validators=[DataRequired(), InputRequired()])
    agencie_name = StringField("Nom de votre agence", validators=[DataRequired(), InputRequired()])
    submit = SubmitField("Créer votre compte")

    def validate_business_number(self, field):
        if VNUser.query.filter_by(vn_business_number=field.data).first():
            raise ValidationError("Ce numéro de régistre de commerce est déjà utilisé !")
