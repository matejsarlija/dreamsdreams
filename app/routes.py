from app import app, db
from app.models import User, Note, UserSchema, NoteSchema
from flask import jsonify, request

note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)

# hello world
@app.route('/')
def hello_world():
    return 'Hello, World!'

# all users
@app.route("/user", methods=["GET"])
def get_user():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)


# endpoint to create new user
@app.route("/user", methods=["POST"])
def add_user():
    username = request.json['username']
    email = request.json['email']

    new_user = User(username, email)

    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user)

# get user detail by id
@app.route("/user/<id>", methods=["GET"])
def user_detail(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)


@app.route("/user/<id>", methods=["PUT"])
def user_update(id):
    user = User.query.get(id)
    username = request.json['username']
    email = request.json['email']

    user.email = email
    user.username = username

    db.session.commit()
    return user_schema.jsonify(user)


@app.route("/user/<id>", methods=["DELETE"])
def user_delete(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()

    return user_schema.jsonify(user)


# ditto for notes
@app.route('/note/')
def note_list():
    all_notes = Note.query.all()
    return jsonify(notes_schema.dump(all_notes))


@app.route('/note/', methods=['POST'])
def create_note():
    body = request.json.get('body', '')
    user_id = request.json.get('user_id', '')


    note = Note(body=body, user_id=user_id)

    db.session.add(note)
    db.session.commit()

    return note_schema.jsonify(note)


@app.route('/note/<int:note_id>/', methods=["GET"])
def note_detail(note_id):
    note = Note.query.get(note_id)
    return note_schema.jsonify(note)


@app.route('/note/<int:note_id>/', methods=['PUT'])
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
