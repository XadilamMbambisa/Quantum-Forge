from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student | advisor
    course = db.Column(db.String(100))  # e.g., BSc in Physics, etc.

    def __repr__(self):
        return f'<User {self.username}>'

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False, default=list)  # Added for options

class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    industry_score = db.Column(db.Integer, default=0)
    research_score = db.Column(db.Integer, default=0)
    academia_score = db.Column(db.Integer, default=0)
    chosen_path = db.Column(db.String(20))

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    advisor_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    start_time = db.Column(db.DateTime)  # Changed to DateTime for proper handling
    status = db.Column(db.String(20), default="booked")

    student = db.relationship('User', foreign_keys=[student_id], backref="student_bookings")
    advisor = db.relationship('User', foreign_keys=[advisor_id], backref="advisor_bookings")

    __table_args__ = (
        db.UniqueConstraint('advisor_id', 'start_time', name='unique_advisor_slot'),
    )