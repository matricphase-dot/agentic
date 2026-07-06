from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    subscription_tier = db.Column(db.String(20), default='free')
    workflows_created = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Workflow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')  # draft, running, paused, completed
    success_rate = db.Column(db.Float, default=0.0)
    revenue_saved = db.Column(db.Float, default=0.0)
    agent_sequence = db.Column(db.JSON)  # ["planner", "researcher", "coder"]
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # Planner, Coder, etc.
    type = db.Column(db.String(20), nullable=False)  # planner, coder, executor
    status = db.Column(db.String(20), default='idle')
    intelligence_score = db.Column(db.Float, default=85.0)
    tasks_completed = db.Column(db.Integer, default=0)
    tasks_failed = db.Column(db.Integer, default=0)
    last_execution = db.Column(db.DateTime)

class SuccessPattern(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workflow_type = db.Column(db.String(50))
    pattern_name = db.Column(db.String(100))
    success_rate = db.Column(db.Float)
    confidence_score = db.Column(db.Float)
    parameters = db.Column(db.JSON)
    discovered_at = db.Column(db.DateTime, default=datetime.utcnow)

class OptimizationTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow.id'))
    variant_a_params = db.Column(db.JSON)
    variant_b_params = db.Column(db.JSON)
    variant_a_success = db.Column(db.Float)
    variant_b_success = db.Column(db.Float)
    winner = db.Column(db.String(10))  # a, b, tie
    test_completed = db.Column(db.DateTime)

class CompetitorIntel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    competitor_name = db.Column(db.String(50))
    feature = db.Column(db.String(100))
    status = db.Column(db.String(20))  # live, planned, missing
    discovered_at = db.Column(db.DateTime, default=datetime.utcnow)
