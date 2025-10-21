from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Question, QuizResult, Booking
from datetime import datetime, timedelta
from sqlalchemy import or_, and_
from career_data import career_data

app = Flask(__name__)

app.config["SECRET_KEY"] = "devkey"  # Replace with secure key for production
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///stemify.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def course_list():
    return [
        "BSc in Physics",
        "BSc in Computer Science",
        "BSc in Applied Mathematics",
        "BSc in Mathematics",
        "BSc in Chemistry"
    ]

def get_field_from_course(course):
    if not course:
        return None
    if "Mathematics" in course:
        return "Mathematics"
    elif "Computer Science" in course:
        return "Computer Science"
    elif "Physics" in course:
        return "Physics"
    elif "Chemistry" in course:
        return "Chemistry"
    return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    courses = course_list()
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        role = request.form.get("role", "student")
        course = request.form.get("course") if role == "student" else None

        if not username or not email or not password:
            flash("Please fill in all required fields.")
            return redirect(url_for("register"))
        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("register"))
        if User.query.filter(or_(User.username == username, User.email == email)).first():
            flash("Username or email already exists.")
            return redirect(url_for("register"))
        if role == "student" and not course:
            flash("Please select a course.")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role=role,
            course=course
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully! Please log in.")
        return redirect(url_for("login"))
    return render_template("register.html", courses=courses)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        identifier = request.form.get("username") or request.form.get("email")
        password = request.form.get("password", "")
        user = User.query.filter(or_(User.email == identifier, User.username == identifier)).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("student_dashboard" if user.role == "student" else "advisor_dashboard"))
        error = "Invalid credentials."
    return render_template("login.html", error=error)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/student/dashboard")
@login_required
def student_dashboard():
    if current_user.role != "student":
        flash("Access denied.")
        return redirect(url_for("index"))
    results = QuizResult.query.filter_by(student_id=current_user.id).all()
    bookings = Booking.query.filter_by(student_id=current_user.id).order_by(Booking.start_time).all()
    return render_template(
        "student_dashboard.html",
        username=current_user.username,
        course=current_user.course,
        results=results,
        bookings=bookings
    )

@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    if current_user.role != "student":
        flash("Access denied.")
        return redirect(url_for("index"))
    questions = Question.query.all()
    if not questions:
        flash("No quiz questions available.")
        return redirect(url_for("student_dashboard"))
    if request.method == "POST":
        scores = {"industry": 0, "research": 0, "academia": 0}
        for q in questions:
            selected = request.form.get(f"q{q.id}")
            if selected in scores:
                scores[selected] += 1
            else:
                flash("Please answer all questions.")
                return redirect(url_for("quiz"))
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

@app.route("/results/<int:result_id>")
@login_required
def results(result_id):
    result = QuizResult.query.get_or_404(result_id)
    if current_user.role == "student" and result.student_id != current_user.id:
        flash("Access denied.")
        return redirect(url_for("student_dashboard"))
    return render_template("results.html", result=result)

@app.route("/career_info/<path_name>")
@login_required
def career_info(path_name):
    if current_user.role != "student":
        flash("Access denied.")
        return redirect(url_for("index"))
    if path_name not in ["industry", "research", "academia"]:
        flash("Invalid career path.")
        return redirect(url_for("student_dashboard"))
    course = current_user.course
    field_key = get_field_from_course(course)
    if not field_key or field_key not in career_data:
        flash("No career information available for your course.")
        return redirect(url_for("student_dashboard"))
    field = career_data[field_key]
    degree_info = field.get("degrees", {}).get(course, {})
    if not degree_info:
        flash("No detailed career information for your degree.")
        return redirect(url_for("student_dashboard"))
    return render_template(
        "career_info.html",
        field=field,
        degree_info=degree_info,
        career_path=path_name,
        course=course
    )

@app.route("/book_session", methods=["GET", "POST"])
@login_required
def book_session():
    if current_user.role != "student":
        flash("Only students can book sessions.")
        return redirect(url_for("index"))
    advisors = User.query.filter_by(role="advisor").all()
    if request.method == "POST":
        try:
            advisor_id = int(request.form.get("advisor_id"))
            start_time_str = request.form.get("start_time", "").strip()
            start_dt = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
            end_dt = start_dt + timedelta(hours=1)
        except (TypeError, ValueError):
            flash("Invalid advisor or time selection.")
            return redirect(url_for("book_session"))
        now = datetime.now()
        if start_dt < now:
            flash("Cannot book in the past.")
            return redirect(url_for("book_session"))
        if start_dt.weekday() >= 5:
            flash("Bookings only available Monday to Friday.")
            return redirect(url_for("book_session"))
        if not (9 <= start_dt.hour < 17):
            flash("Bookings must be within office hours (9AM-5PM).")
            return redirect(url_for("book_session"))
        advisor_conflicts = Booking.query.filter(
            Booking.advisor_id == advisor_id,
            Booking.status.in_(["booked", "rescheduled"]),
            or_(
                and_(Booking.start_time <= start_dt, start_dt < Booking.start_time + timedelta(hours=1)),
                and_(start_dt <= Booking.start_time, Booking.start_time < end_dt)
            )
        ).first()
        student_conflicts = Booking.query.filter(
            Booking.student_id == current_user.id,
            Booking.status.in_(["booked", "rescheduled"]),
            or_(
                and_(Booking.start_time <= start_dt, start_dt < Booking.start_time + timedelta(hours=1)),
                and_(start_dt <= Booking.start_time, Booking.start_time < end_dt)
            )
        ).first()
        if advisor_conflicts:
            flash("This advisor has a conflicting booking.")
            return redirect(url_for("book_session"))
        if student_conflicts:
            flash("You have a conflicting booking.")
            return redirect(url_for("book_session"))
        booking = Booking(
            student_id=current_user.id,
            advisor_id=advisor_id,
            start_time=start_dt,
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
    if current_user.role == "student" and booking.student_id != current_user.id:
        flash("You cannot cancel another student's booking.")
        return redirect(url_for("student_dashboard"))
    booking.status = "cancelled"
    db.session.commit()
    flash("Session cancelled.")
    return redirect(url_for("student_dashboard"))

@app.route("/reschedule_session/<int:booking_id>", methods=["POST"])
@login_required
def reschedule_session(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if current_user.role == "student" and booking.student_id != current_user.id:
        flash("You cannot reschedule another student's booking.")
        return redirect(url_for("student_dashboard"))
    new_time_str = request.form.get("new_time", "").strip()
    try:
        new_dt = datetime.fromisoformat(new_time_str.replace("Z", "+00:00"))
        new_end_dt = new_dt + timedelta(hours=1)
    except ValueError:
        flash("Invalid new time.")
        return redirect(url_for("student_dashboard"))
    now = datetime.now()
    if new_dt < now:
        flash("Cannot reschedule to the past.")
        return redirect(url_for("student_dashboard"))
    if new_dt.weekday() >= 5:
        flash("Reschedule to weekdays only.")
        return redirect(url_for("student_dashboard"))
    if not (9 <= new_dt.hour < 17):
        flash("Reschedule within office hours (9AM-5PM).")
        return redirect(url_for("student_dashboard"))
    advisor_conflicts = Booking.query.filter(
        Booking.advisor_id == booking.advisor_id,
        Booking.id != booking.id,
        Booking.status.in_(["booked", "rescheduled"]),
        or_(
            and_(Booking.start_time <= new_dt, new_dt < Booking.start_time + timedelta(hours=1)),
            and_(new_dt <= Booking.start_time, Booking.start_time < new_end_dt)
        )
    ).first()
    student_conflicts = Booking.query.filter(
        Booking.student_id == current_user.id,
        Booking.id != booking.id,
        Booking.status.in_(["booked", "rescheduled"]),
        or_(
            and_(Booking.start_time <= new_dt, new_dt < Booking.start_time + timedelta(hours=1)),
            and_(new_dt <= Booking.start_time, Booking.start_time < new_end_dt)
        )
    ).first()
    if advisor_conflicts or student_conflicts:
        flash("Conflict at new time.")
        return redirect(url_for("student_dashboard"))
    booking.start_time = new_dt
    booking.status = "rescheduled"
    db.session.commit()
    flash("Session rescheduled!")
    return redirect(url_for("student_dashboard"))

@app.route("/advisor/dashboard")
@login_required
def advisor_dashboard():
    if current_user.role != "advisor":
        flash("Access denied.")
        return redirect(url_for("index"))
    bookings = Booking.query.filter_by(advisor_id=current_user.id).order_by(Booking.start_time).all()
    return render_template("advisor_dashboard.html", username=current_user.username, bookings=bookings)

@app.route("/view_sessions")
@login_required
def view_sessions():
    if current_user.role != "advisor":
        flash("Only advisors can view sessions.")
        return redirect(url_for("index"))
    bookings = Booking.query.filter_by(advisor_id=current_user.id).order_by(Booking.start_time).all()
    return render_template("view_sessions.html", bookings=bookings)

@app.route("/advisor_cancel/<int:booking_id>", methods=["POST"])
@login_required
def advisor_cancel(booking_id):
    if current_user.role != "advisor":
        abort(403)
    booking = Booking.query.get_or_404(booking_id)
    if booking.advisor_id != current_user.id:
        flash("You cannot cancel this session.")
        return redirect(url_for("advisor_dashboard"))
    booking.status = "cancelled"
    db.session.commit()
    flash("Session cancelled.")
    return redirect(url_for("advisor_dashboard"))

@app.route("/advisor_reschedule/<int:booking_id>", methods=["POST"])
@login_required
def advisor_reschedule(booking_id):
    if current_user.role != "advisor":
        abort(403)
    booking = Booking.query.get_or_404(booking_id)
    if booking.advisor_id != current_user.id:
        flash("You cannot reschedule this session.")
        return redirect(url_for("advisor_dashboard"))
    new_time_str = request.form.get("new_time", "").strip()
    try:
        new_dt = datetime.fromisoformat(new_time_str.replace("Z", "+00:00"))
        new_end_dt = new_dt + timedelta(hours=1)
    except ValueError:
        flash("Invalid new time.")
        return redirect(url_for("advisor_dashboard"))
    now = datetime.now()
    if new_dt < now:
        flash("Cannot reschedule to the past.")
        return redirect(url_for("advisor_dashboard"))
    if new_dt.weekday() >= 5:
        flash("Reschedule to weekdays only.")
        return redirect(url_for("advisor_dashboard"))
    if not (9 <= new_dt.hour < 17):
        flash("Reschedule within office hours (9AM-5PM).")
        return redirect(url_for("advisor_dashboard"))
    advisor_conflicts = Booking.query.filter(
        Booking.advisor_id == current_user.id,
        Booking.id != booking.id,
        Booking.status.in_(["booked", "rescheduled"]),
        or_(
            and_(Booking.start_time <= new_dt, new_dt < Booking.start_time + timedelta(hours=1)),
            and_(new_dt <= Booking.start_time, Booking.start_time < new_end_dt)
        )
    ).first()
    student_conflicts = Booking.query.filter(
        Booking.student_id == booking.student_id,
        Booking.id != booking.id,
        Booking.status.in_(["booked", "rescheduled"]),
        or_(
            and_(Booking.start_time <= new_dt, new_dt < Booking.start_time + timedelta(hours=1)),
            and_(new_dt <= Booking.start_time, Booking.start_time < new_end_dt)
        )
    ).first()
    if advisor_conflicts or student_conflicts:
        flash("Conflict at new time.")
        return redirect(url_for("advisor_dashboard"))
    booking.start_time = new_dt
    booking.status = "rescheduled"
    db.session.commit()
    flash("Session rescheduled!")
    return redirect(url_for("advisor_dashboard"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)