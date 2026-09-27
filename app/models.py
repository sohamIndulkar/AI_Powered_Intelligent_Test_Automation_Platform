from flask_login import UserMixin
from . import db
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    test_runs = db.relationship('TestRun', backref='user', lazy=True, cascade="all, delete-orphan")
    test_cases = db.relationship('TestCase', backref='user', lazy=True, cascade="all, delete-orphan")

class TestRun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url_tested = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    results_json = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class TestCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    commands_json = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # NEW COLUMN to store baseline images as a JSON object
    baseline_images_json = db.Column(db.Text, nullable=True)