from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ \
                os.path.join(basedir, 'db.sqlite3')

db = SQLAlchemy(app)
ma = Marshmallow(app)


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
