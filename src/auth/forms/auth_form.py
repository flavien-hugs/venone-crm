from flask_wtf import FlaskForm
from wtforms.validators import (
    Email,
    Length,
    EqualTo,
    DataRequired,
    ValidationError,
)
from wtforms import StringField, PasswordField, SubmitField, BooleanField

from ... import db
from ..models import VNUser


class LoginForm(FlaskForm):
    addr_email = StringField(
        "Adresse Email",
        validators=[
            DataRequired(), Length(1, 64),
            Email(message="Entrer une adresse email valide."),
        ],
    )
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    remember_me = BooleanField('Gardez-moi connecté')
    submit = SubmitField("Se connecter")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Ancien mot de passe', validators=[DataRequired()])
    password_one = PasswordField('Nouveau mot de passe', validators=[DataRequired()])
    password_two = PasswordField(
        'Confirmer le mot de passe',
        validators=[
            DataRequired(),
            EqualTo('password_two', message='Les deux mots de passe ne correspondent pas.')
        ]
    )
    submit = SubmitField('Mettre à jour votre mot de passe')


class PasswordResetRequestForm(FlaskForm):
    addr_email = StringField('Votre adresse e-mail', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('Demander une réinitialisation du mot de passe')


class PasswordResetForm(FlaskForm):
    password_one = PasswordField('Nouveau mot de passe', validators=[DataRequired()])
    password_two = PasswordField(
        'Confirmer le mot de passe',
        validators=[
            DataRequired(),
            EqualTo('password_two', message='Les deux mots de passe ne correspondent pas.')
        ]
    )
    submit = SubmitField('Réinitialiser le mot de passe')
