from wtforms.validators import (
    Email,
    Length,
    EqualTo,
    Regexp,
    DataRequired,
    InputRequired
)
from wtforms import StringField, PasswordField, SelectField

from ..constants import COUNTRY


class FormMixin:
    fullname = StringField(
        "Nom et prénom",
        validators=[
            DataRequired(),
            InputRequired()
        ]
    )
    addr_email = StringField(
        "Adresse email",
        validators=[
            DataRequired(), InputRequired(),
            Email(message="Entrer une adresse email valide."),
        ],
    )
    phonenumber_one = StringField(
        "Numéro de téléphone",
        validators=[DataRequired(), InputRequired()]
    )
    cni_number = StringField("Numéro de votre CNI", validators=[DataRequired(), InputRequired()])
    country = SelectField("Pays/Région", choices=COUNTRY, coerce=str)
    password = PasswordField(
        "Mot de passe",
        validators=[
            DataRequired(), InputRequired(),
            Length(min=6, max=20, message="Choisissez un mot de passe plus fort."),
        ],
    )
    confirm_password = PasswordField(
        "Confirmer le mot de passe",
        validators=[
            DataRequired(), InputRequired(),
            EqualTo(
                "password",
                message="Les deux mots de passe ne correspondent pas."
            ),
        ],
    )
