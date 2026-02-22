from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, InputRequired, ValidationError

from src.auth.forms.default_form import FormMixin
from src.auth.models import VNUser
from src.constants import GENDER


class AgencieSignupForm(FormMixin, FlaskForm):
    gender = SelectField("Genre", choices=GENDER, coerce=str)
    fullname = StringField(
        "Nom du gestionnaire",
        render_kw={"required": True},
        validators=[DataRequired(), InputRequired()],
    )
    business_number = StringField(
        "N° de votre régistre de commerce",
        render_kw={"required": True},
        validators=[DataRequired(), InputRequired()],
    )
    agencie_name = StringField(
        "Nom de l'entreprise",
        render_kw={"required": True},
        validators=[DataRequired(), InputRequired()],
    )
    submit = SubmitField("Ouvrir mon compte")

    def validate_business_number(self, field):
        if VNUser.query.filter_by(vn_business_number=field.data).first():
            raise ValidationError(
                "Ce numéro de régistre de commerce est déjà utilisé !"
            )
