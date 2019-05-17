from flask_httpauth import HTTPBasicAuth
from WebApp.models import User
from flask_login import AnonymousUserMixin
from flask import g
from WebApp.app.api_1_0 import api
from WebApp.app.main.errors import forbidden_error

auth = HTTPBasicAuth()

@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')

@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')

@auth.verify_password
def verify_password(email, password):
    if email == '':
        g.current_user = AnonymousUserMixin()
        return True
    user = User.query.filter_by(email = email).first()
    if not user:
        return False
    g.current_user = user
    return user.verify_password(password)