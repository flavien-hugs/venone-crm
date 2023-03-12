from flask_wtf import FlaskForm
from src.dashboard.forms.default_form import DefaultForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import InputRequired
from wtforms.validators import ValidationError


class CompanySettingForm(DefaultForm, FlaskForm):

    fullname = StringField(label="Nom du gestionnaire", validators=[InputRequired()])
    agencie_name = StringField(
        label="Nom de votre agence", validators=[DataRequired(), InputRequired()]
    )
    business_number = StringField(
        label="N° Registre de commerce", validators=[DataRequired(), InputRequired()]
    )
    cni_number = StringField(
        label="N° de votre CNI", validators=[DataRequired(), InputRequired()]
    )
    location = StringField(label="Situation géographique", validators=[InputRequired()])
    submit = SubmitField(label="Enregistrer les modifications")

    def validate_fullname(self, fullname):
        excluded_chars = "*?!'^+%&/()=}][{$#"
        for char in self.fullname.data:
            if char in excluded_chars:
                raise ValidationError(f"Character {char} is not allowed in fullname.")
