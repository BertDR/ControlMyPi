from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from WebApp.models import User


class ServerInfoForm(FlaskForm):
    PublicIP = StringField('PublicIP')
    PrivateIP = StringField('PrivateIP')
    Temperature = StringField('Temperature')
    AppRootPath = StringField('AppRootPath')

