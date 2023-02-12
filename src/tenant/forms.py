from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms import SelectField, DateField
from wtforms import IntegerField, Form, FormField
from wtforms.validators import DataRequired, Length, Optional

from src.constants import GENDER
from src.constants import HOUSE_TYPES, DEFAULT_HOUSE_TYPES
from src.dashboard.forms.default_form import DefaultForm


class HouseForm(FlaskForm):

    house_type = SelectField(label="Type de location", choices=HOUSE_TYPES, coerce=str, default=DEFAULT_HOUSE_TYPES, validators=[DataRequired()])
    house_number_or_room = IntegerField(label="Nombre de pièces", validators=[DataRequired(), Length(min=1, max=10)])
    house_rent = IntegerField(label="Loyer/mois", validators=[DataRequired()])
    house_guaranty = IntegerField(label="Caution", validators=[DataRequired(), Length(min=1, max=5)])
    house_month = IntegerField(label="Nombre de mois de caution", validators=[DataRequired()])
    house_address = StringField(label="Situation géographique", validators=[DataRequired()])


class TenantForm(FlaskForm):

    gender = SelectField(label="Genre", choices=GENDER, coerce=str)
    fullname = StringField(label="Nom & prénom", validators=[DataRequired()])
    phonenumber_one = StringField(label="Numéro de téléphone 1", validators=[DataRequired()])
    phonenumber_two = StringField(label="Numéro de téléphone 2", validators=[Optional()])
    cni_number = StringField(label="N° de votre CNI", validators=[DataRequired()])
    addr_email = StringField(label="Adresse e-mail", validators=[Optional()])
    profession = StringField(label="Profession", validators=[DataRequired()])
    parent_name = StringField(label="Nom d'un parent", validators=[Optional()])
    location = StringField(label="Lieu de résidence", validators=[DataRequired()])
    birthdate = DateField(label="Date de naissance", validators=[Optional()])


class HouseOwnerForm(DefaultForm, FlaskForm):

    fullname = StringField(label="Nom & prénom", validators=[DataRequired()])
    addr_email = StringField(label="Adresse e-mail", validators=[Optional()])
    cni_number = StringField(label="N° de votre CNI", validators=[DataRequired()])
    phonenumber_one = StringField(label="Numéro de téléphone 1", validators=[DataRequired()])
    profession = StringField(label="Profession", validators=[Optional()])
    parent_name = StringField(label="Nom d'un parent", validators=[Optional()])
    location = StringField(label="Lieu de résidence", validators=[DataRequired()])
