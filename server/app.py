from flask import Flask, request, session
from flask_migrate import Migrate

from models import db, bcrypt, User, Note


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "development-secret-key"

db.init_app(app)
bcrypt.init_app(app)

migrate = Migrate(app, db)


def user_to_dict(user):
    return {
        "id": user.id,
        "username": user.username
    }

def get_current_user():
    user_id = session.get("user_id")

    if not user_id:
        return None

    return db.session.get(User, user_id) 

def note_to_dict(note):
    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "created_at": note.created_at.isoformat() if note.created_at else None,
        "updated_at": note.updated_at.isoformat() if note.updated_at else None,
        "user_id": note.user_id
    }

@app.get("/notes")
def get_notes():
    user = get_current_user()

    if not user:
        return {"errors": ["Authentication required."]}, 401

    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
    except ValueError:
        return {"errors": ["page and per_page must be integers."]}, 400

    if page < 1 or per_page < 1:
        return {"errors": ["page and per_page must be greater than 0."]}, 400

    pagination = Note.query.filter_by(
        user_id=user.id
    ).order_by(
        Note.id
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return {
        "notes": [note_to_dict(note) for note in pagination.items],
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages
    }, 200

@app.post("/notes")
def create_note():
    user = get_current_user()

    if not user:
        return {"errors": ["Authentication required."]}, 401

    data = request.get_json()

    title = data.get("title") if data else None
    content = data.get("content") if data else None

    errors = []

    if not title:
        errors.append("Title is required.")

    if not content:
        errors.append("Content is required.")

    if errors:
        return {"errors": errors}, 400

    note = Note(
        title=title,
        content=content,
        user_id=user.id
    )

    db.session.add(note)
    db.session.commit()

    return note_to_dict(note), 201

@app.patch("/notes/<int:id>")
def update_note(id):
    user = get_current_user()

    if not user:
        return {"errors": ["Authentication required."]}, 401

    note = Note.query.filter_by(
        id=id,
        user_id=user.id
    ).first()

    if not note:
        return {"errors": ["Note not found."]}, 404

    data = request.get_json()

    if "title" in data:
        note.title = data["title"]

    if "content" in data:
        note.content = data["content"]

    db.session.commit()

    return note_to_dict(note), 200

@app.delete("/notes/<int:id>")
def delete_note(id):
    user = get_current_user()

    if not user:
        return {"errors": ["Authentication required."]}, 401

    note = Note.query.filter_by(
        id=id,
        user_id=user.id
    ).first()

    if not note:
        return {"errors": ["Note not found."]}, 404

    db.session.delete(note)
    db.session.commit()

    return {}, 204

@app.post("/signup")
def signup():
    data = request.get_json()

    username = data.get("username") if data else None
    password = data.get("password") if data else None
    password_confirmation = (
        data.get("password_confirmation") if data else None
    )

    errors = []

    if not username:
        errors.append("Username is required.")

    if not password:
        errors.append("Password is required.")

    if password != password_confirmation:
        errors.append("Passwords do not match.")

    if User.query.filter_by(username=username).first():
        errors.append("Username already exists.")

    if errors:
        return {"errors": errors}, 400

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(
        username=username,
        password_hash=password_hash
    )

    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id

    return user_to_dict(user), 201


@app.post("/login")
def login():
    data = request.get_json()

    username = data.get("username") if data else None
    password = data.get("password") if data else None

    user = User.query.filter_by(username=username).first()

    if not user or not bcrypt.check_password_hash(
        user.password_hash,
        password or ""
    ):
        return {"errors": ["Invalid username or password."]}, 401

    session["user_id"] = user.id

    return user_to_dict(user), 200


@app.get("/check_session")
def check_session():
    user_id = session.get("user_id")

    if not user_id:
        return {}, 200

    user = db.session.get(User, user_id)

    if not user:
        session.clear()
        return {}, 200

    return user_to_dict(user), 200


@app.delete("/logout")
def logout():
    session.clear()
    return {}, 200


if __name__ == "__main__":
    app.run(port=5555, debug=True)
