from src.constants import DEVISE
from src.constants import DEVISE_DEFAULT
from src.constants import GENDER
from src.constants import GENDER_DEFAULT
from wtforms import SelectField
from wtforms import StringField
from wtforms.validators import Optional
from wtforms.validators import InputRequired


class DefaultForm:

    gender = SelectField(
        label="Genre", choices=GENDER, coerce=str, default=GENDER_DEFAULT,
        validators=[Optional()]
    )
    phonenumber_two = StringField(label="Numéro de téléphone 2", validators=[Optional()])
    devise = SelectField(
        label="Devise", render_kw={"required": True}, validators=[InputRequired()], choices=DEVISE, coerce=str, default=DEVISE_DEFAULT
    )
