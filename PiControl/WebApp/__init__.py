from flask import Flask

from .config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler
from flask_bootstrap import Bootstrap
from flask_moment import Moment

db = SQLAlchemy()
bootstrap = Bootstrap()
moment = Moment()
login = LoginManager()
migrate = Migrate()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config.configs[config_name])
    config.configs[config_name].init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    login.login_view = 'auth.login'
    login_manager.init_app(app)

    moment.init_app(app)
# attach routes and custom error pages here
    from WebApp.app.main import main as main_blueprint
    app.register_blueprint(main_blueprint )

    from WebApp.app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from WebApp.app.api_1_0 import api as api
    app.register_blueprint(api, url_prefix='/api/v1.0')


    return app