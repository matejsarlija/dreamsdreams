from datetime import datetime
from app import db, ma


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    notes = db.relationship(
        'Note',
        backref='author',
        cascade='all, delete, delete-orphan',
        single_parent=True,
        lazy='dynamic',
        order_by='desc(Note.timestamp)'
    )

    """def __init__(self, username, email):
        self.username = username
        self.email = email"""

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    """def __init__(self, body):
        self.body = body"""

    def __repr__(self):
        return '<Note {}>'.format(self.body)


class Following(db.Model):
    __tablename__ = "follow"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User


class NoteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Note





