from flask_wtf import FlaskForm
from src.auth.models import VNUser
from wtforms import BooleanField
from wtforms import PasswordField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import EqualTo
from wtforms.validators import Length
from wtforms.validators import ValidationError


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
    new_password = PasswordField("Nouveau mot de passe", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirmer le mot de passe",
        validators=[
            DataRequired(),
            EqualTo(
                "new_password", message="Les deux mots de passe ne correspondent pas."
            ),
        ],
    )


class PasswordResetRequestForm(FlaskForm):
    addr_email = StringField(
        "Votre adresse e-mail", validators=[DataRequired(), Length(1, 64), Email()]
    )
    submit = SubmitField("Demander une réinitialisation du mot de passe")


class PasswordResetForm(FlaskForm):
    new_password = PasswordField("Nouveau mot de passe", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirmer le mot de passe",
        validators=[
            DataRequired(),
            EqualTo(
                "confirm_password",
                message="Les deux mots de passe ne correspondent pas.",
            ),
        ],
    )


class ChangeEmailForm(FlaskForm):
    addr_email = StringField(
        "Nouvel adresse email", validators=[DataRequired(), Length(1, 64), Email()]
    )
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Mise à jour de l'adresse e-mail")

    def validate_addr_email(self, field):
        if VNUser.query.filter_by(vn_user_addr_email=field.data.lower()).first():
            raise ValidationError("L'adresse électronique est déjà enregistrée.")
