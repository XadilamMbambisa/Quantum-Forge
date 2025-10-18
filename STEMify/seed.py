from myapp import app, db
from models import User, Question
from werkzeug.security import generate_password_hash

def seed_data():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Add default users
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

        db.session.add_all([student, advisor])

        # Add sample questions for each category
        questions = [
            # Industry
            Question(text="Do you enjoy working on practical, hands-on problems?", category="industry"),
            Question(text="Do you like solving real-world challenges in a team?", category="industry"),
            Question(text="Do you prefer applied projects over theoretical ones?", category="industry"),

            # Research
            Question(text="Do you like solving abstract problems and publishing findings?", category="research"),
            Question(text="Do you enjoy analyzing data and discovering new patterns?", category="research"),
            Question(text="Are you interested in conducting experiments to test theories?", category="research"),

            # Academia
            Question(text="Do you enjoy teaching and mentoring others?", category="academia"),
            Question(text="Do you like preparing lectures or presenting ideas?", category="academia"),
            Question(text="Are you motivated by helping students learn and succeed?", category="academia")
        ]

        db.session.add_all(questions)
        db.session.commit()

        print("✅ Database seeded with default users and multiple questions per category.")

if __name__ == "__main__":
    seed_data()
