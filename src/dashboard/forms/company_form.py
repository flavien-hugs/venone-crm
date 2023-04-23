from flask_wtf import FlaskForm
from src.dashboard.forms.default_form import DefaultForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import Optional
from wtforms.validators import InputRequired
from wtforms.validators import ValidationError


class CompanySettingForm(DefaultForm, FlaskForm):

    fullname = StringField(label="Nom du gestionnaire",  render_kw={"required": True}, validators=[InputRequired()])
    agencie_name = StringField(
        label="Nom de votre agence",  render_kw={"required": True}, validators=[InputRequired()]
    )
    location = StringField(label="Situation géographique", validators=[Optional()])
    submit = SubmitField(label="Enregistrer les modifications")

    def validate_fullname(self, fullname):
        excluded_chars = "*?!'^+%&/()=}][{$#"
        for char in self.fullname.data:
            if char in excluded_chars:
                raise ValidationError(f"Character {char} is not allowed in fullname.")
