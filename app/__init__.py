from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
ma = Marshmallow(app)

from app import routes, models

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
