# Imports the core libraries required for running the app, including the Flask library itself

# Various libraries, plus our own configuration (loaded from config.py)
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)           # Create Flask app
app.config.from_object(Config)  # Apply configuration
db = SQLAlchemy(app)            # SQLAlchemy for DB
migrate = Migrate(app, db)      # DB migration tool
lm = LoginManager(app)          # User login handler

from app import routes, models, filters, errors
