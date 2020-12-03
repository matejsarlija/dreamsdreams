from werkzeug.exceptions import abort
from app import app, db
from app.auth import basic_auth, token_auth
from app.models import User, Note, UserSchema, NoteSchema
from flask import jsonify, request, url_for

note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)

# hello world
@app.route('/')
def hello_world():
    return jsonify("Hello, World")

# get a token for the registered user
@app.route('/token', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return jsonify({'token': token})

# delete your token
@app.route('/token', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    token = token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204

# all users
@app.route("/user", methods=["GET"])
@token_auth.login_required
def get_user():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)


# endpoint to create new user
@app.route("/user", methods=["POST"])
def add_user():
    username = request.json['username']
    password = request.json['password']
    if username is None or password is None:
        abort(400)
    if User.query.filter_by(username=username).first() is not None:
        abort(400)
    new_user = User(username=username)
    new_user.hash_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({ 'username': new_user.username }), 201, {'Location': url_for('get_user', id = new_user.id, _external = True)}

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

# follow another user by username, protected by token auth
@app.route('/follow/<username>', methods=['POST'])
@token_auth.login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    current_user = token_auth.current_user()
    if user is None:
        abort(400)
    if user == current_user:
        return jsonify("Can't follow yourself"), 400
    current_user.follow(user)
    db.session.commit()
    return '', 204

# unfollow another user by username, protected by token auth
@app.route('/unfollow/<username>', methods=['POST'])
@token_auth.login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    current_user = token_auth.current_user()
    if user is None:
        abort(400)
    if user == current_user:
        return jsonify("Can't follow yourself"), 400
    current_user.unfollow(user)
    db.session.commit()
    return '', 204


# all notes / Public feed
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
