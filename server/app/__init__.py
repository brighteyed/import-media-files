from flask import Flask
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app_db = SQLAlchemy()

Base = declarative_base()
db_metadata = Base.metadata

