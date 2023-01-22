from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import InputRequired
from wtforms.validators import ValidationError

from ... import db
from ..constants import GENDER
from ..models import VNUser
from .form import FormMixin


class AgencieSignupForm(FormMixin, FlaskForm):

    gender = SelectField("Genre", choices=GENDER, coerce=str)
    fullname = StringField(
        "Nom du gestionnaire", validators=[DataRequired(), InputRequired()]
    )
    business_number = StringField(
        "N° de votre régistre de commerce", validators=[DataRequired(), InputRequired()]
    )
    agencie_name = StringField(
        "Nom de votre agence", validators=[DataRequired(), InputRequired()]
    )
    submit = SubmitField("Créer votre compte")

    def validate_business_number(self, field):
        if db.session.query(VNUser).filter_by(vn_business_number=field.data).first():
            raise ValidationError(
                "Ce numéro de régistre de commerce est déjà utilisé !"
            )
