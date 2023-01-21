from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms import PasswordField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import EqualTo
from wtforms.validators import Length
from wtforms.validators import ValidationError

from ..models import VNUser


class LoginForm(FlaskForm):
    addr_email = StringField(
        "Adresse Email",
        validators=[
            DataRequired(),
            Length(1, 64),
            Email(message="Entrer une adresse email valide."),
        ],
    )
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    remember_me = BooleanField("Se souvenir de moi")
    submit = SubmitField("Se connecter")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Ancien mot de passe", validators=[DataRequired()])
    password_one = PasswordField("Nouveau mot de passe", validators=[DataRequired()])
    password_two = PasswordField(
        "Confirmer le mot de passe",
        validators=[
            DataRequired(),
            EqualTo(
                "password_two", message="Les deux mots de passe ne correspondent pas."
            ),
        ],
    )
    submit = SubmitField("Mettre à jour votre mot de passe")


class PasswordResetRequestForm(FlaskForm):
    addr_email = StringField(
        "Votre adresse e-mail", validators=[DataRequired(), Length(1, 64), Email()]
    )
    submit = SubmitField("Demander une réinitialisation du mot de passe")


class PasswordResetForm(FlaskForm):
    password_one = PasswordField("Nouveau mot de passe", validators=[DataRequired()])
    password_two = PasswordField(
        "Confirmer le mot de passe",
        validators=[
            DataRequired(),
            EqualTo(
                "password_two", message="Les deux mots de passe ne correspondent pas."
            ),
        ],
    )
    submit = SubmitField("Réinitialiser le mot de passe")


class ChangeEmailForm(FlaskForm):
    addr_email = StringField(
        "Nouvel adresse email", validators=[DataRequired(), Length(1, 64), Email()]
    )
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Mise à jour de l'adresse e-mail")

    def validate_addr_email(self, field):
        if VNUser.query.filter_by(vn_user_addr_email=field.data.lower()).first():
            raise ValidationError("L'adresse électronique est déjà enregistrée.")
