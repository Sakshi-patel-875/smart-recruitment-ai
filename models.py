from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# Recruiter users
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Matching sessions
class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    job_description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    candidates = db.relationship("Candidate", backref="session", lazy=True)

# Candidate results
class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("session.id"))
    name = db.Column(db.String(200))
    score = db.Column(db.Float)
    experience = db.Column(db.Integer)
    recommendation = db.Column(db.String(50))