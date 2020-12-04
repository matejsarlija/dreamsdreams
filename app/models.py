from passlib.apps import custom_app_context as pwd_context
import base64
import os
from datetime import datetime, timedelta
from app import db, ma

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
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
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )

    """def __init__(self, username, email):
        self.username = username
        self.email = email"""

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Note.query.join(
            followers, (followers.c.followed_id == Note.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Note.query.filter_by(user_id = self.id)
        return followed.union(own).order_by(Note.timestamp.desc())


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    image_path = db.Column(db.String(256))
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





