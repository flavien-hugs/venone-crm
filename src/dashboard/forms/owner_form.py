from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from flask_wtf.file import FileField
from src.dashboard.forms.default_form import DefaultForm
from wtforms import DateField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class OwnerSettingForm(DefaultForm, FlaskForm):
    fullname = StringField(label="Nom & prénom", validators=[DataRequired()])
    profession = StringField(label="Votre profession", validators=[DataRequired()])
    parent_name = StringField("Nom d'un parent", validators=[DataRequired()])
    location = StringField(label="Lieu de résidence", validators=[DataRequired()])
    birthdate = DateField(label="Date de naissance")
    cni_number = StringField(label="N° de votre CNI", validators=[DataRequired()])
    picture = FileField(
        "Update Avatar", validators=[FileAllowed(["jpg", "jpeg", "png", "svg"])]
    )
    submit = SubmitField(label="Enregistrer les modifications")
