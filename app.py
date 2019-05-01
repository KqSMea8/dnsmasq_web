from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config


app = Flask(__name__)

app.config.from_object(Config)
Config.init_app(app)

db = SQLAlchemy(app)


import views
app.register_blueprint(views.mod)
