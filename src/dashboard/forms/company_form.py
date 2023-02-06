from flask_wtf import FlaskForm
from src.dashboard.forms.default_form import DefaultForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import InputRequired


class CompanySettingForm(DefaultForm, FlaskForm):

    fullname = StringField("Nom du gestionnaire", validators=[InputRequired()])
    agencie_name = StringField(
        "Nom de votre agence", validators=[DataRequired(), InputRequired()]
    )
    business_number = StringField(
        "N° Registre de commerce", validators=[DataRequired(), InputRequired()]
    )
    cni_number = StringField(
        "N° de votre CNI", validators=[DataRequired(), InputRequired()]
    )
    location = StringField("Situation géographique", validators=[InputRequired()])
    submit = SubmitField("Ouvrir mon compte")
