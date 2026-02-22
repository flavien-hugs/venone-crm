from flask_wtf import FlaskForm
from wtforms import DateField, StringField, SubmitField
from wtforms.validators import InputRequired, Optional

from src.dashboard.forms.default_form import DefaultForm


class OwnerSettingForm(DefaultForm, FlaskForm):
    fullname = StringField(
        label="Nom & prénom", render_kw={"required": True}, validators=[InputRequired()]
    )
    profession = StringField(label="Votre profession", validators=[Optional()])
    parent_name = StringField("Nom d'un parent", validators=[Optional()])
    location = StringField(label="Lieu de résidence", validators=[Optional()])
    birthdate = DateField(label="Date de naissance", validators=[Optional()])
    submit = SubmitField(label="Enregistrer les modifications")
