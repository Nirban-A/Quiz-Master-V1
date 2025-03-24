from flask import Flask
from application.database import db
from application.models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///quiz_master_v1.sqlite3"

#we are initialising the SQLalchemy object db (which initialises the db) with the flask application app
db.init_app(app) 


with app.app_context():
    db.create_all()
