from myapp import app, db
from models import User, Question
from werkzeug.security import generate_password_hash

def seed_data():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Add users
        student = User(
            username="student1",
            email="student@example.com",
            password_hash=generate_password_hash("password123"),
            role="student"
        )
        advisor = User(
            username="advisor1",
            email="advisor@example.com",
            password_hash=generate_password_hash("password123"),
            role="advisor"
        )

        db.session.add(student)
        db.session.add(advisor)

        # Add sample questions
        q1 = Question(text="Do you enjoy working on practical, hands-on problems?", category="industry")
        q2 = Question(text="Do you like solving abstract problems and publishing findings?", category="research")
        q3 = Question(text="Do you enjoy teaching and mentoring others?", category="academia")

        db.session.add_all([q1, q2, q3])

        db.session.commit()
        print("✅ Database seeded with default users and questions.")

if __name__ == "__main__":
    seed_data()
