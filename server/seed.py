from faker import Faker

from app import app
from models import db, bcrypt, User, Note

fake = Faker()

with app.app_context():
    print("Clearing existing data...")

    Note.query.delete()
    User.query.delete()
    db.session.commit()

    print("Creating users...")

    users = []

    for i in range(3):
        user = User(
            username=f"user{i + 1}",
            password_hash=bcrypt.generate_password_hash(
                "password123"
            ).decode("utf-8")
        )

        db.session.add(user)
        users.append(user)

    db.session.commit()

    print("Creating notes...")

    for user in users:
        for _ in range(5):
            note = Note(
                title=fake.sentence(nb_words=4),
                content=fake.paragraph(),
                user_id=user.id
            )

            db.session.add(note)

    db.session.commit()

    print("Seed data created successfully.")
