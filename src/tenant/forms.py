from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired

from src.dashboard.forms.default_form import DefaultForm


class HouseOwnerForm(DefaultForm, FlaskForm):

    fullname = StringField("Nom & prénom", validators=[DataRequired()])
    addr_email = StringField("Adresse e-mail")
    phonenumber_one = StringField("Numéro de téléphone 1")
    profession = StringField("Profession", validators=[DataRequired()])
    parent_name = StringField("Nom d'un parent", validators=[DataRequired()])
    location = StringField("Lieu de résidence", validators=[DataRequired()])
    cni_number = StringField("N° de votre CNI", validators=[DataRequired()])
    submit = SubmitField("Valider")
