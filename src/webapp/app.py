from flask import Flask
from flask_sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = 'static/bingo_uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bingo.db'
db = SQLAlchemy(app)

from webapp.routes import *

if __name__ == "__main__":
    app.run(debug=True)