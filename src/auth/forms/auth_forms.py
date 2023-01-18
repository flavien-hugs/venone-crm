from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms.validators import (
    Email,
    Length,
    EqualTo,
    Regexp,
    DataRequired,
    ValidationError,
)
from wtforms import(
    StringField, SelectField,
    PasswordField, SubmitField, BooleanField
)

from ... import db
from ..models import VNRole, VNUser


def validate_login(form, field):
    user = form.get_user()

    if user is None:
        raise validators.ValidationError(
            "Cet utilisateur n'existe pas ou le compte a été désactivé")

    if user.vn_user_password != form.password.data:
        raise validators.ValidationError('Mot de passe invalide')


class LoginForm(FlaskForm):
    addr_email = StringField(
        "Adresse Email",
        validators=[
            DataRequired(), Length(1, 64),
            Email(message="Entrer une adresse email valide."),
        ],
    )
    password = PasswordField("Mot de passe", validators=[DataRequired(), validate_login])
    submit = SubmitField("Se connecter")

    def get_user(self):
        return db.session.query(VNUser).filter_by(addr_email=self.addr_email.data).first()


# =============================================================
#                     House Owner Form
# =============================================================

class OwnerHouseSignupForm(FlaskForm):

    gender = SelectField("Genre", coerce=str)
    fullname = StringField(
        "Nom et prénom",
        validators=[
            DataRequired(),
            Length(4, 80),
        ]
    )
    addr_email = StringField(
        "Adresse email",
        validators=[
            DataRequired(),
            Length(1, 64),
            Email(message="Entrer une adresse email valide."),
        ],
    )
    phonenumber_one = StringField(
        "Numéro de téléphone",
        validators=[DataRequired()]
    )
    cni_number = StringField(
        "Numéro de votre CNI",
        validators=[DataRequired()],
    )
    country = SelectField("Pays/Région", coerce=str)
    current_password = PasswordField(
        "Mot de passe",
        validators=[
            DataRequired(),
            Length(min=6, max=20, message="Choisissez un mot de passe plus fort."),
        ],
    )
    confirm_password = PasswordField(
        "Confirmer le mot de passe",
        validators=[
            DataRequired(),
            EqualTo(
                "current_password",
                message="Les deux mots de passe ne correspondent pas."
            ),
        ],
    )
    submit = SubmitField("S'inscrire")

    def validate_email(self, field):
        user = db.session.query(VNUser).filter_by(addr_email=self.addr_email.data).one_or_none()
        if user:
            raise ValidationError(
                f"""
                Cet adresse '{field.data.lower()}' est déjà utilisé.
                Veuillez choisir un autre nom !
                """
            )


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    password = PasswordField('New password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm new password', validators=[DataRequired()])
    submit = SubmitField('Update Password')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')


class ChangeEmailForm(FlaskForm):
    email = StringField('New Email', validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')
