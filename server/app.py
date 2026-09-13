from flask import Flask, request, session
from flask_migrate import Migrate

from models import db, bcrypt, User


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
