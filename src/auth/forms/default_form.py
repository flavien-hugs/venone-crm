from wtforms import PasswordField
from wtforms import SelectField
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import EqualTo
from wtforms.validators import InputRequired
from wtforms.validators import Length
from wtforms.validators import ValidationError

from ... import db
from ..constants import COUNTRY
from ..models import VNUser


class FormMixin:
    addr_email = StringField(
        "Adresse email",
        validators=[
            DataRequired(),
            InputRequired(),
            Email(message="Entrer une adresse email valide."),
        ],
    )
    phonenumber_one = StringField(
        "Numéro de téléphone", validators=[DataRequired(), InputRequired()]
    )
    country = SelectField("Pays/Région", choices=COUNTRY, coerce=str)
    password = PasswordField(
        "Mot de passe",
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=6, max=20, message="Choisissez un mot de passe plus fort."),
        ],
    )
    confirm_password = PasswordField(
        "Confirmer le mot de passe",
        validators=[
            DataRequired(),
            InputRequired(),
            EqualTo("password", message="Les deux mots de passe ne correspondent pas."),
        ],
    )

    def validate_addr_email(self, field):
        user = (
            db.session.query(VNUser)
            .filter_by(vn_user_addr_email=field.data.lower())
            .first()
        )
        if user:
            raise ValidationError(
                f"""
                Cet email '{field.datar}!r' est déjà utilisé.
                Veuillez choisir un autre nom !
                """
            )

    def validate_phonenumber_one(self, field):
        if (
            db.session.query(VNUser)
            .filter_by(vn_user_phonenumber_one=field.data)
            .first()
        ):
            raise ValidationError("Ce numéro est déjà utilisé.")
