# Full Auth Flask Backend - Productivity App

A secure Flask REST API for a productivity notes application. The backend uses Flask sessions for authentication and allows authenticated users to create, view, update, and delete their own notes.

## Features

* User signup with password confirmation
* Secure password hashing with Flask-Bcrypt
* Session-based authentication
* Login and logout
* Check current session
* Protected Notes API
* User-owned notes
* CRUD operations for notes
* Pagination for notes
* Flask-SQLAlchemy database models
* Flask-Migrate database migrations
* Faker seed data
* Automated pytest tests

## Technologies

* Python 3.8.13
* Flask 2.2.2
* Flask-SQLAlchemy 3.0.3
* Flask-Migrate 4.0.0
* Flask-Bcrypt 1.0.1
* Flask-RESTful 0.3.9
* Marshmallow 3.20.1
* Faker 15.3.2
* Pytest 7.2.0
* SQLite

## Installation

From the `server` directory:

```bash
pipenv install
```

## Database Setup

Apply the existing database migrations:

```bash
pipenv run flask --app app db upgrade
```

Check the current migration:

```bash
pipenv run flask --app app db current
```

## Seed the Database

Populate the database with sample users and notes:

```bash
pipenv run python seed.py
```

The seed script creates:

* 3 users
* 15 notes
* 5 notes for each user

The seeded users use the password:

```text
password123
```

Passwords are stored as Bcrypt hashes rather than plain text.

## Run the Server

Start the Flask development server:

```bash
pipenv run python app.py
```

The API runs on:

```text
http://localhost:5555
```

Port 5555 is used to match the sessions client proxy configuration.

## Authentication Endpoints

### Sign Up

**POST `/signup`**

Request:

```json
{
  "username": "newuser",
  "password": "password123",
  "password_confirmation": "password123"
}
```

Successful response:

```json
{
  "id": 1,
  "username": "newuser"
}
```

### Login

**POST `/login`**

Request:

```json
{
  "username": "newuser",
  "password": "password123"
}
```

A successful login creates a Flask session.

### Check Session

**GET `/check_session`**

Returns the currently authenticated user.

If no user is logged in, the API returns an empty object.

### Logout

**DELETE `/logout`**

Clears the current Flask session.

## Notes Endpoints

All Notes endpoints require authentication.

### Get Notes

**GET `/notes`**

Returns notes belonging only to the currently authenticated user.

Pagination can be specified using `page` and `per_page`:

```text
GET /notes?page=1&per_page=10
```

Example response:

```json
{
  "notes": [],
  "page": 1,
  "per_page": 10,
  "total": 0,
  "pages": 0
}
```

### Create a Note

**POST `/notes`**

Request:

```json
{
  "title": "My Note",
  "content": "This is my note content."
}
```

The authenticated user's ID is automatically assigned to the note.

### Update a Note

**PATCH `/notes/<id>`**

Request:

```json
{
  "title": "Updated Note",
  "content": "Updated note content."
}
```

Users can only update their own notes.

### Delete a Note

**DELETE `/notes/<id>`**

Users can only delete their own notes.

A successful deletion returns HTTP `204 No Content`.

## Note Model

Each note contains:

* `id`
* `title`
* `content`
* `created_at`
* `updated_at`
* `user_id`

The `user_id` associates each note with its owner.

## Authorization

The Notes API is protected by Flask session authentication.

Users can only access notes associated with their own `user_id`. Attempting to modify or delete another user's note returns HTTP `404`.

## Testing

Run the automated test suite with:

```bash
pipenv run pytest
```

The tests cover:

* Signup
* Password hashing
* Login
* Session checking
* Logout
* Authentication protection
* Note creation
* Note retrieval
* Note updates
* Note deletion
* User ownership
* Pagination

## Project Structure

```text
server/
├── app.py
├── models.py
├── seed.py
├── Pipfile
├── Pipfile.lock
├── README.md
├── migrations/
│   ├── versions/
│   └── ...
└── tests/
    ├── __init__.py
    └── test_app.py
```

## Client Applications

This repository also contains two client applications:

* `client-with-sessions/` - React client using Flask sessions
* `client-with-jwt/` - React client prepared for JWT authentication

The backend in this project uses **Flask sessions**.

Author 
Maurine Wanjira
