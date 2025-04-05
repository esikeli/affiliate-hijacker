from app import db
from datetime import datetime
from flask_login import UserMixin

class Project(db.Model):
    """Model for affiliate hijacker projects"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(50), default="new")  # new, analyzed, funnel_generated, completed
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Stored as JSON strings
    analysis = db.Column(db.Text)  # JSON string of page analysis
    funnel_data = db.Column(db.Text)  # JSON string of funnel data
    email_sequence = db.Column(db.Text)  # JSON string of email sequence
    
    def __repr__(self):
        return f'<Project {self.name}>'

class FunnelPage(db.Model):
    """Model for funnel pages"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    page_type = db.Column(db.String(50), nullable=False)  # main, upsell, downsell
    content = db.Column(db.Text)  # HTML content
    order = db.Column(db.Integer, default=0)
    
    # Relationship
    project = db.relationship('Project', backref=db.backref('pages', lazy=True))
    
    def __repr__(self):
        return f'<FunnelPage {self.name} ({self.page_type})>'

class EmailTemplate(db.Model):
    """Model for email templates"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, default=0)
    
    # Relationship
    project = db.relationship('Project', backref=db.backref('emails', lazy=True))
    
    def __repr__(self):
        return f'<EmailTemplate {self.subject}>'

# Optional User model if authentication is needed
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    
    # Relationship with projects
    projects = db.relationship('Project', backref='owner', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
