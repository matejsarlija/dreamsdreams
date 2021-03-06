from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
import os
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


# delete (revoke) your token
@app.route('/token', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    token = token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204


# all users, for test purposes
@app.route("/user", methods=["GET"])
@token_auth.login_required
def get_user():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)


# endpoint to create new user a.k.a the register page
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

    return jsonify({'username': new_user.username}), 201, {'Location': url_for('get_user', id = new_user.id, _external = True)}


# some admin type options, commented out for now
"""


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
"""


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
    page = request.args.get('page', 1, type=int)
    all_notes = Note.query.order_by(Note.timestamp.desc()).paginate(
        page, 3, False
    )
    return jsonify(notes_schema.dump(all_notes.items))


# notes from users you follow plus your own / Private feed
@app.route('/feed', methods=['GET'])
@token_auth.login_required
def private_feed():
    page = request.args.get('page', 1, type=int)
    current_user = token_auth.current_user()
    followed_notes = current_user.followed_posts().paginate(
        page, 3, False)
    return jsonify(notes_schema.dump(followed_notes.items))


# create a Note "tweet"
@app.route('/note/', methods=['POST'])
@token_auth.login_required
def create_note():
    current_user = token_auth.current_user()
    file = request.files['image']
    body = request.form['body']
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        note = Note(body=body, image_path=file_path, user_id=current_user.id)
    else:
        # body = request.json.get('body', '')
        note = Note(body=body, user_id=current_user.id)
    db.session.add(note)
    db.session.commit()

    return note_schema.jsonify(note)


# get a tweet by id, if you're the author
@app.route('/note/<int:note_id>/', methods=["GET"])
@token_auth.login_required
def note_detail(note_id):
    current_user = token_auth.current_user()
    note = Note.query.get(note_id)
    if note.user_id == current_user.id:
        return note_schema.jsonify(note)
    else:
        abort(401)


# update own tweet
@app.route('/note/<int:note_id>/', methods=['PUT'])
@token_auth.login_required
def update_note(note_id):
    current_user = token_auth.current_user()
    body = request.json.get('body', '')

    note = Note.query.get(note_id)
    if note.user_id != current_user.id:
        abort(401)

    note.body = body
    db.session.add(note)
    db.session.commit()

    return note_schema.jsonify(note)


# delete own tweets by id
@app.route('/note/<int:note_id>/', methods=["DELETE"])
@token_auth.login_required
def delete_note(note_id):
    current_user = token_auth.current_user()
    note = Note.query.get(note_id)

    if note.user_id != current_user.id:
        abort(401)

    db.session.delete(note)
    db.session.commit()

    return '', 204
