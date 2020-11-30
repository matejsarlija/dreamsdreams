from flask import jsonify, request
from datetime import datetime
from app import ma, app
from app import db


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique =True)
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

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Note(db.Model):
    __tablename__ = "note"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, body):
        self.body = body

    def __repr__(self):
        return '<Note {}>'.format(self.body)

class Following(db.Model):
    __tablename__ = "follow"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('username', 'email')
        model = User


class NoteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Note


note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)


# endpoint to create new user
@app.route("/user", methods=["POST"])
def add_user():
    username = request.json['username']
    email = request.json['email']

    new_user = User(username, email)

    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user)


# endpoint to show all users
@app.route("/user", methods=["GET"])
def get_user():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result.data)


# endpoint to get user detail by id
@app.route("/user/<id>", methods=["GET"])
def user_detail(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)


# endpoint to update user
@app.route("/user/<id>", methods=["PUT"])
def user_update(id):
    user = User.query.get(id)
    username = request.json['username']
    email = request.json['email']

    user.email = email
    user.username = username

    db.session.commit()
    return user_schema.jsonify(user)


# endpoint to delete user
@app.route("/user/<id>", methods=["DELETE"])
def user_delete(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()

    return user_schema.jsonify(user)


@app.route('/note/')
def note_list():
    all_notes = Note.query.all()
    return jsonify(notes_schema.dump(all_notes))


@app.route('/note/', methods=['POST'])
def create_note():
    body = request.json.get('body', '')

    note = Note(body=body)

    db.session.add(note)
    db.session.commit()

    return note_schema.jsonify(note)


@app.route('/note/<int:note_id>/', methods=["GET"])
def note_detail(note_id):
    note = Note.query.get(note_id)
    return note_schema.jsonify(note)


@app.route('/note/<int:note_id>/', methods=['PATCH'])
def update_note(note_id):
    body = request.json.get('body', '')

    note = Note.query.get(note_id)

    note.body = body

    db.session.add(note)
    db.session.commit()

    return note_schema.jsonify(note)


@app.route('/note/<int:note_id>/', methods=["DELETE"])
def delete_note(note_id):
    note = Note.query.get(note_id)

    db.session.delete(note)
    db.session.commit()

    return note_schema.jsonify(note)
