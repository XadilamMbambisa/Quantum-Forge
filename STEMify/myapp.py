from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Question, QuizResult, Booking
import os

app = Flask(__name__)

# Config
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "devkey")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///stemify.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------ Routes ------------------

# Landing page
@app.route("/")
def index():
    return render_template("index.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.role == "student":
                return redirect(url_for("student_dashboard"))
            return redirect(url_for("advisor_dashboard"))
        error = "Invalid credentials."
    return render_template("login.html", error=error)

# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

# Create/register account

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        role = request.form["role"]

        # Validate password match
        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("register"))

        # Check if username or email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Username or email already exists.")
            return redirect(url_for("register"))

        # Hash the password and create the new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password, role=role)

        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


# ------------------ Student Routes ------------------

@app.route("/student/dashboard")
@login_required
def student_dashboard():
    if current_user.role != "student":
        flash("Access denied.")
        return redirect(url_for("index"))
    results = QuizResult.query.filter_by(student_id=current_user.id).all()
    bookings = Booking.query.filter_by(student_id=current_user.id).all()
    return render_template("student_dashboard.html", username=current_user.username,
                           results=results, bookings=bookings)

@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    if current_user.role != "student":
        flash("Access denied.")
        return redirect(url_for("index"))

    questions = Question.query.all()

    if request.method == "POST":
        scores = {"industry": 0, "research": 0, "academia": 0}

        for q in questions:
            selected_category = request.form.get(f"q{q.id}")
            if selected_category in scores:
                scores[selected_category] += 1

        best = max(scores, key=scores.get)

        result = QuizResult(
            student_id=current_user.id,
            industry_score=scores["industry"],
            research_score=scores["research"],
            academia_score=scores["academia"],
            chosen_path=best
        )
        db.session.add(result)
        db.session.commit()

        return redirect(url_for("results", result_id=result.id))

    return render_template("quiz.html", questions=questions)

@app.route("/book_session", methods=["GET", "POST"])
@login_required
def book_session():
    if current_user.role != "student":
        flash("Only students can book sessions.")
        return redirect(url_for("index"))

    advisors = User.query.filter_by(role="advisor").all()

    if request.method == "POST":
        advisor_id = request.form["advisor_id"]
        start_time = request.form["start_time"]

        # Check for conflicts
        existing_booking = Booking.query.filter_by(
            advisor_id=advisor_id, start_time=start_time
        ).first()

        student_conflict = Booking.query.filter_by(
            student_id=current_user.id, start_time=start_time
        ).first()

        if existing_booking:
            flash("This advisor is already booked at that time. Please choose another slot.")
            return redirect(url_for("book_session"))

        if student_conflict:
            flash("You already have a session booked at that time.")
            return redirect(url_for("book_session"))

        booking = Booking(
            student_id=current_user.id,
            advisor_id=advisor_id,
            start_time=start_time,
            status="booked"
        )
        db.session.add(booking)
        db.session.commit()
        flash("Session booked successfully!")
        return redirect(url_for("student_dashboard"))

    return render_template("book_session.html", advisors=advisors)

    @app.route("/cancel_session/<int:booking_id>", methods=["POST"])
@login_required
def cancel_session(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.student_id != current_user.id:
        flash("You cannot cancel another student's booking.")
        return redirect(url_for("student_dashboard"))

    booking.cancel()
    db.session.commit()
    flash("Your session has been cancelled.")
    return redirect(url_for("student_dashboard"))


@app.route("/reschedule_session/<int:booking_id>", methods=["POST"])
@login_required
def reschedule_session(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.student_id != current_user.id:
        flash("You cannot reschedule another student's booking.")
        return redirect(url_for("student_dashboard"))

    new_time = request.form["new_time"]

    # Check for conflicts
    existing_booking = Booking.query.filter_by(
        advisor_id=booking.advisor_id, start_time=new_time
    ).first()
    student_conflict = Booking.query.filter_by(
        student_id=current_user.id, start_time=new_time
    ).first()

    if existing_booking or student_conflict:
        flash("This time slot is already booked. Choose another one.")
        return redirect(url_for("student_dashboard"))

    booking.reschedule(new_time)
    db.session.commit()
    flash("Session successfully rescheduled!")
    return redirect(url_for("student_dashboard"))


# ------------------ Advisor Routes ------------------

@app.route("/advisor/dashboard")
@login_required
def advisor_dashboard():
    if current_user.role != "advisor":
        flash("Access denied.")
        return redirect(url_for("index"))
    return render_template("advisor_dashboard.html", username=current_user.username)

@app.route("/view_sessions")
@login_required
def view_sessions():
    if current_user.role != "advisor":
        flash("Only advisors can view sessions.")
        return redirect(url_for("index"))

    bookings = Booking.query.filter_by(advisor_id=current_user.id).all()
    return render_template("view_sessions.html", bookings=bookings)

# ------------------ Initialize DB & Run ------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()






