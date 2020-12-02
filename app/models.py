from datetime import datetime
from app import db, ma


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

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
    followed = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers')
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



class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User


class NoteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Note





