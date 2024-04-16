import os
from flask import Flask, render_template, request, session, redirect
from flask_cors import CORS
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_login import LoginManager
from .config import Config
from .models import db

app = Flask(__name__, static_folder='../react-app/build', static_url_path='/')

app.config.from_object(Config)

db.init_app(app)
Migrate(app, db)

CORS(app)
