from flask_wtf import FlaskForm
from src.dashboard.forms.default_form import DefaultForm
from wtforms import DateField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import InputRequired
from wtforms.validators import Optional


class OwnerSettingForm(DefaultForm, FlaskForm):
    fullname = StringField(
        label="Nom & prénom", render_kw={"required": True}, validators=[InputRequired()]
    )
    profession = StringField(label="Votre profession", validators=[Optional()])
    parent_name = StringField("Nom d'un parent", validators=[Optional()])
    location = StringField(label="Lieu de résidence", validators=[Optional()])
    birthdate = DateField(label="Date de naissance", validators=[Optional()])
    submit = SubmitField(label="Enregistrer les modifications")
