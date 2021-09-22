from flask import Flask

# New imports
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from dotenv import load_dotenv
import os
import urllib
from app import app_config

# force loading of environment variables
load_dotenv('.flaskenv')

# Get the environment variables from .flaskenv
PASSWORD = os.environ.get('DATABASE_PASSWORD')
USERNAME = os.environ.get('DATABASE_USERNAME')
DB_NAME = os.environ.get('DATABASE_NAME')
server = 'bookddb.database.windows.net'

# we're using mssql and pyodbc modules instead, this is what
# MicroSoft SQL servers utilize

# these statements establish the uri config below
dbstr = "DRIVER={SQL Server};Database="+DB_NAME+";SERVER="+server+";UID="+USERNAME+";PWD="+PASSWORD
dbstr = urllib.parse.quote_plus(dbstr)
dbstr = "mssql+pyodbc:///?odbc_connect=%s" % dbstr


# start app, secret key can be changed later
app = Flask(__name__)
app.config.from_object(app_config)
Session(app)

app.config['SECRET_KEY'] = 'capstone'

# Add DB config
app.config['SQLALCHEMY_DATABASE_URI'] = dbstr

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= True

app.config.update(
        MAIL_SERVER = 'smtp.gmail.com',
        MAIL_PORT = 465,
        MAIL_USE_TLS = False,
        MAIL_USE_SSL = True, 
        MAIL_USERNAME = 'bookdapp203@gmail.com',
        MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD'),
        MAIL_DEFAULT_SENDER = ('Book\'d', 'bookdapp203@gmail.com'),
        SECRET_KEY = 'capstone')

# Create database connection and associate it with the Flask application
db = SQLAlchemy(app)

from app import routes, models
from app.models import Users

