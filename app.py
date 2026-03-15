from flask import Flask, redirect, render_template, request, session
from resume_parser import extract_text, extract_skills
from job_parser import extract_job_skills, extract_job_text_from_file
from matcher import calculate_match
import os
from report_generator import generate_report
from flask import send_file
from resume_parser import extract_experience
from job_parser import extract_required_experience
from accuracy import update_accuracy, get_accuracy
from models import db, User, Session, Candidate
from flask_login import LoginManager
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

if not os.path.exists("resumes"):
    os.makedirs("resumes")

app = Flask(__name__)

app.config["SECRET_KEY"] = "secret123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
@login_required
def home():
    return render_template("home.html")

@app.route("/match", methods=["GET", "POST"])
@login_required
def index():
    results = []
    job_skills = []

    total_resumes = 0
    avg_match = 0
    highest_match = 0
    top_gaps = []

    # ⭐ If results exist from previous run, load them
    if "LAST_RESULTS" in app.config:
        results = app.config["LAST_RESULTS"]
        job_skills = app.config["JOB_SKILLS"]

    if request.method == "POST":
        results = []
        top_gaps = []
        job_text = request.form["jobdesc"].strip()
        job_file = request.files.get("jobfile")

        # If JD file uploaded, use it instead
        if job_file and job_file.filename != "":
           jd_path = os.path.join("resumes", job_file.filename)
           job_file.save(jd_path)
           job_text = extract_job_text_from_file(jd_path)

        resume_files = request.files.getlist("resumes")
    
        # ⭐ Validation check
        if not job_text or not resume_files or resume_files[0].filename == "":
           error_msg = "Please provide job description and upload at least one resume."
           return render_template(
            "index.html",
            results=results,
            job_skills=job_skills,
            error=error_msg
        )

        # ⭐ CREATE MATCHING SESSION HERE
        session = Session(
            user_id=current_user.id,
            job_description=job_text
        )

        db.session.add(session)
        db.session.commit()

        # Extract job skills
        job_skills = extract_job_skills(job_text)

        # ⭐ Extract required experience from job
        required_exp = extract_required_experience(job_text)

        for resume_file in resume_files:
            resume_path = os.path.join("resumes", resume_file.filename)
            resume_file.save(resume_path)

            resume_text = extract_text(resume_path)
            resume_skills = extract_skills(resume_text)

            # ⭐ Extract candidate experience from resume
            candidate_exp = extract_experience(resume_text)

            # ⭐ Calculate experience score
            exp_score = 0
            if required_exp > 0:
                exp_score = min(candidate_exp / required_exp, 1) * 100

            # ⭐ Skill score (already working)
            skill_score = calculate_match(resume_skills, job_skills)

            # ⭐ Final weighted score (80% skills + 20% experience)
            match_score = round((0.8 * skill_score) + (0.2 * exp_score), 2)

            # Recommendation logic
            if match_score >= 80:
               recommendation = "Recommended"
            elif match_score >= 50:
               recommendation = "Consider"
            else:
               recommendation = "Not Suitable"

            matched = list(set(resume_skills) & set(job_skills))
            missing = list(set(job_skills) - set(resume_skills))

            explanation = []

            if match_score >= 80:
                explanation.append("Strong skill alignment")

            if candidate_exp >= 2:
                explanation.append("Relevant experience")

            if len(missing) == 0:
                explanation.append("No critical skill gaps")

            results.append({
            "name": resume_file.filename,
            "score": match_score,
            "experience": candidate_exp,
            "skills": resume_skills,
            "matched": matched,
            "missing": missing,
            "recommendation": recommendation,
            "explanation": explanation
            })

            candidate = Candidate(
            session_id=session.id,
            name=resume_file.filename,
            score=match_score,
            experience=candidate_exp,
            recommendation=recommendation
            )

            db.session.add(candidate)

        db.session.commit()

        # Sort results
        results = sorted(results, key=lambda x: x["score"], reverse=True)

        from collections import Counter

        # GAP ANALYSIS
        all_missing = []

        for r in results:
            all_missing.extend(r["missing"])

        gap_counter = Counter(all_missing)

        top_gaps = [skill for skill, count in gap_counter.most_common(3)]

        # Save for PDF report
        app.config["LAST_RESULTS"] = results
        app.config["JOB_SKILLS"] = job_skills

        total_resumes = len(results)
        avg_match = round(sum(r["score"] for r in results) / total_resumes, 2) if total_resumes > 0 else 0
        highest_match = max([r["score"] for r in results], default=0)

    return render_template("index.html", results=results, job_skills=job_skills, error=None, chart_labels=[r["name"] for r in results],
    chart_scores=[r["score"] for r in results],
    total_resumes=total_resumes,
    avg_match=avg_match,
    highest_match=highest_match,
    top_gaps=top_gaps)

@app.route("/download_report")
def download_report():
    report_path = "match_report.pdf"
    generate_report(app.config["LAST_RESULTS"], app.config["JOB_SKILLS"], report_path)
    return send_file(report_path, as_attachment=True)

@app.route("/accuracy")
@login_required
def accuracy():
    acc = get_accuracy()
    return f"<h2>System Match Accuracy: {acc}%</h2><br><a href='/match'>Go Back</a>"

@app.route("/validate", methods=["POST"])
def validate():
    selected = request.form.getlist("correct")
    total = int(request.form["total"])

    correct = len(selected)
    update_accuracy(total, correct)

    return "<h3>Validation Saved!</h3><a href='/accuracy'>View Accuracy</a>"

@app.route("/reset")
def reset():
    app.config.pop("LAST_RESULTS", None)
    app.config.pop("JOB_SKILLS", None)
    return redirect("/match")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
           return "Email already registered. Please login."

        user = User(name=name, email=email, password=password)

        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect("/match")

        return "Invalid login"

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

@app.route("/history")
@login_required
def history():

    sessions = Session.query.filter_by(user_id=current_user.id)\
        .order_by(Session.created_at.desc())\
        .all()

    return render_template("history.html", sessions=sessions)

@app.route("/session/<int:session_id>")
@login_required
def session_detail(session_id):

    session_data = Session.query.filter_by(
    id=session_id,
    user_id=current_user.id
    ).first_or_404()

    candidates = Candidate.query.filter_by(session_id=session_id)\
        .order_by(Candidate.score.desc())\
        .all()

    return render_template(
        "session_detail.html",
        session=session_data,
        candidates=candidates
    )

if __name__ == "__main__":
    app.run(debug=True)
