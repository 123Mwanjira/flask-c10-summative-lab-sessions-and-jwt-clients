import pytest

from app import app, db
from models import User, Note


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.drop_all()
        db.create_all()

        yield app.test_client()

        db.session.remove()
        db.drop_all()


def signup(client, username="testuser", password="password123"):
    return client.post(
        "/signup",
        json={
            "username": username,
            "password": password,
            "password_confirmation": password
        }
    )


def login(client, username="testuser", password="password123"):
    return client.post(
        "/login",
        json={
            "username": username,
            "password": password
        }
    )


def test_signup_hashes_password(client):
    response = signup(client)

    assert response.status_code == 201
    assert response.json["username"] == "testuser"

    with app.app_context():
        user = User.query.filter_by(username="testuser").first()

        assert user is not None
        assert user.password_hash != "password123"


def test_login_and_check_session(client):
    signup(client)

    response = login(client)

    assert response.status_code == 200
    assert response.json["username"] == "testuser"

    response = client.get("/check_session")

    assert response.status_code == 200
    assert response.json["username"] == "testuser"


def test_logout(client):
    signup(client)

    response = client.delete("/logout")

    assert response.status_code == 200
    assert response.json == {}

    response = client.get("/check_session")

    assert response.status_code == 200
    assert response.json == {}


def test_notes_require_authentication(client):
    response = client.get("/notes")

    assert response.status_code == 401


def test_create_and_get_note(client):
    signup(client)

    response = client.post(
        "/notes",
        json={
            "title": "Test Note",
            "content": "Test content"
        }
    )

    assert response.status_code == 201
    assert response.json["title"] == "Test Note"

    response = client.get("/notes")

    assert response.status_code == 200
    assert response.json["total"] == 1
    assert len(response.json["notes"]) == 1


def test_update_note(client):
    signup(client)

    create = client.post(
        "/notes",
        json={
            "title": "Original",
            "content": "Original content"
        }
    )

    note_id = create.json["id"]

    response = client.patch(
        f"/notes/{note_id}",
        json={
            "title": "Updated",
            "content": "Updated content"
        }
    )

    assert response.status_code == 200
    assert response.json["title"] == "Updated"
    assert response.json["content"] == "Updated content"


def test_user_cannot_modify_another_users_note(client):
    signup(client, "user1")

    create = client.post(
        "/notes",
        json={
            "title": "Private Note",
            "content": "Private content"
        }
    )

    note_id = create.json["id"]

    client.delete("/logout")

    signup(client, "user2")

    response = client.patch(
        f"/notes/{note_id}",
        json={
            "title": "Hacked",
            "content": "Hacked content"
        }
    )

    assert response.status_code == 404


def test_pagination(client):
    signup(client)

    for i in range(5):
        client.post(
            "/notes",
            json={
                "title": f"Note {i}",
                "content": f"Content {i}"
            }
        )

    response = client.get("/notes?page=1&per_page=2")

    assert response.status_code == 200
    assert response.json["total"] == 5
    assert response.json["pages"] == 3
    assert len(response.json["notes"]) == 2

    response = client.get("/notes?page=2&per_page=2")

    assert response.status_code == 200
    assert len(response.json["notes"]) == 2


def test_delete_note(client):
    signup(client)

    create = client.post(
        "/notes",
        json={
            "title": "Delete Me",
            "content": "This note will be deleted."
        }
    )

    note_id = create.json["id"]

    response = client.delete(f"/notes/{note_id}")

    assert response.status_code == 204

    response = client.get("/notes")

    assert response.status_code == 200
    assert response.json["total"] == 0


def test_user_cannot_delete_another_users_note(client):
    signup(client, "user1")

    create = client.post(
        "/notes",
        json={
            "title": "Private Note",
            "content": "Private content"
        }
    )

    note_id = create.json["id"]

    client.delete("/logout")

    signup(client, "user2")

    response = client.delete(f"/notes/{note_id}")

    assert response.status_code == 404