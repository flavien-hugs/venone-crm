from flask_wtf import FlaskForm
from src.dashboard.forms.default_form import DefaultForm
from wtforms import DateField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class OwnerSettingForm(DefaultForm, FlaskForm):
    fullname = StringField("Nom & prénom", validators=[DataRequired()])
    profession = StringField("Votre profession", validators=[DataRequired()])
    parent_name = StringField("Nom d'un parent", validators=[DataRequired()])
    location = StringField("Lieu de résidence", validators=[DataRequired()])
    birthdate = DateField("Date de naissance")
    cni_number = StringField("N° de votre CNI", validators=[DataRequired()])
    submit = SubmitField("Enregistrer les modifications")
