# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config


app = Flask(__name__)

app.config.from_object(Config)
Config.init_app(app)

db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.login_view = 'general.login'
login_manager.session_protection = None
login_manager.init_app(app)


import views
app.register_blueprint(views.mod)
