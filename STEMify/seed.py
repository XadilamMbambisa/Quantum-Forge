from myapp import app, db
from models import User, Question
from werkzeug.security import generate_password_hash

def seed_data():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Users
        student = User(username="student1", email="student@example.com",
                       password_hash=generate_password_hash("password123"), role="student")
        advisor = User(username="advisor1", email="advisor@example.com",
                       password_hash=generate_password_hash("password123"), role="advisor")
        db.session.add_all([student, advisor])

        # Sample questions with options
        questions = [
            Question(
                text="What would your ideal workday look like?",
                options=[
                    {"text": "Solve problems with peers and meet deadlines", "category": "industry"},
                    {"text": "Do research in a lab with a group", "category": "research"},
                    {"text": "Learn more about my field and do periodic research", "category": "academia"}
                ]
            ),
            Question(
                text="Which activity sounds most appealing?",
                options=[
                    {"text": "Design and implement practical solutions", "category": "industry"},
                    {"text": "Analyze data and explore new ideas", "category": "research"},
                    {"text": "Teach and mentor others while doing research", "category": "academia"}
                ]
            ),
            Question(
                text="How do you prefer to spend your time?",
                options=[
                    {"text": "Working on hands-on projects with immediate results", "category": "industry"},
                    {"text": "Conducting experiments or simulations to test theories", "category": "research"},
                    {"text": "Preparing lessons and guiding others in learning", "category": "academia"}
                ]
            ),
            Question(
                text="What motivates you most in a career?",
                options=[
                    {"text": "Solving real-world problems and meeting deadlines", "category": "industry"},
                    {"text": "Discovering new knowledge and publishing findings", "category": "research"},
                    {"text": "Helping others learn and advancing knowledge in your field", "category": "academia"}
                ]
            ),
            Question(
                text="How do you prefer to work?",
                options=[
                    {"text": "In collaborative teams on practical tasks", "category": "industry"},
                    {"text": "Independently or in small research groups exploring ideas", "category": "research"},
                    {"text": "With students and colleagues in a teaching/research environment", "category": "academia"}
                ]
            ),
            Question(
                text="What is your preferred type of problem-solving?",
                options=[
                    {"text": "Immediate, tangible solutions to practical problems", "category": "industry"},
                    {"text": "Abstract analysis and experimental investigation", "category": "research"},
                    {"text": "Theoretical explanations and educational applications", "category": "academia"}
                ]
            ),
            Question(
                text="Which of the following best describes your career goal?",
                options=[
                    {"text": "Work in a company and contribute to projects with deadlines", "category": "industry"},
                    {"text": "Pursue research in a specialized field", "category": "research"},
                    {"text": "Become a professor or academic mentor", "category": "academia"}
                ]
            )
        ]

        db.session.add_all(questions)
        db.session.commit()

if __name__ == "__main__":
    seed_data()
