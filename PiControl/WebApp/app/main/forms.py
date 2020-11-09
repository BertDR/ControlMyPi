from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, NumberRange
from WebApp.models import User

class ServerConfigForm(FlaskForm):
    cameraOrientation = IntegerField('Camera Orientation',validators=[NumberRange(0,360, 'Please specify a value from 0 through 360' )])
    temperatureDelta = IntegerField('Temperature adjustment')
    submit = SubmitField('Submit')

class ServerInfoForm(FlaskForm):
    PublicIP = StringField('PublicIP')
    PrivateIP = StringField('PrivateIP')
    Temperature = StringField('Temperature')
    AppRootPath = StringField('AppRootPath')

class PicturesForm(FlaskForm):
    submit = SubmitField('Take Picture')