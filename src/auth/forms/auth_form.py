from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from src.auth.models import VNUser


class LoginForm(FlaskForm):
    email_or_phone = StringField(
        "Adresse e-mail ou numéro de téléphone",
        render_kw={"required": True},
        validators=[DataRequired()],
    )
    password = PasswordField(
        "Mot de passe", render_kw={"required": True}, validators=[DataRequired()]
    )
    remember_me = BooleanField("Se souvenir de moi")
    submit = SubmitField("Se connecter")


class PasswordResetForm(FlaskForm):
    new_password = PasswordField(
        "Nouveau mot de passe",
        render_kw={"required": True},
        validators=[DataRequired()],
    )
    confirm_password = PasswordField(
        "Confirmer le mot de passe",
        render_kw={"required": True},
        validators=[
            DataRequired(),
            EqualTo(
                "confirm_password",
                message="Les deux mots de passe ne correspondent pas.",
            ),
        ],
    )


class ChangePasswordForm(PasswordResetForm):
    old_password = PasswordField(
        "Ancien mot de passe", render_kw={"required": True}, validators=[DataRequired()]
    )


class PasswordResetRequestForm(FlaskForm):
    addr_email = StringField(
        "Votre adresse e-mail",
        render_kw={"required": True},
        validators=[
            DataRequired(),
            Length(1, 64),
            Email(message="Entrer une adresse email valide."),
        ],
    )
    submit = SubmitField("envoyer le lien de réinitialisation")


class ChangeEmailForm(FlaskForm):
    addr_email = StringField(
        "Nouvel adresse email",
        render_kw={"required": True},
        validators=[DataRequired(), Length(1, 64), Email()],
    )
    password = PasswordField(
        "Mot de passe", render_kw={"required": True}, validators=[DataRequired()]
    )
    submit = SubmitField("Mise à jour de l'adresse e-mail")

    def validate_addr_email(self, field):
        if VNUser.query.filter_by(vn_user_addr_email=field.data.lower()).first():
            raise ValidationError("L'adresse électronique est déjà enregistrée.")
