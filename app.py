import os
import logging
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from sqlalchemy.orm import DeclarativeBase
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set up database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure SQLite database by default
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///affiliate_hijacker.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with SQLAlchemy
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import routes after app initialization to avoid circular imports
from scraper import scrape_url
from ai_engine import analyze_page, generate_copy
from funnel_generator import generate_funnel
from email_generator import generate_email_sequence
import models

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))

# Create tables on app startup
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """Home page route"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page showing saved projects"""
    projects = models.Project.query.all()
    return render_template('dashboard.html', projects=projects)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze an affiliate URL"""
    url = request.form.get('url')
    name = request.form.get('name', f"Project {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    if not url:
        flash("Please provide a URL to analyze", "danger")
        return redirect(url_for('index'))
    
    try:
        # Extract content from the URL
        logger.debug(f"Scraping URL: {url}")
        content = scrape_url(url)
        
        if not content:
            flash("Could not extract content from the provided URL", "danger")
            return redirect(url_for('index'))
        
        # Analyze the scraped content
        logger.debug("Analyzing content with AI")
        analysis = analyze_page(content, url)
        
        # Create a new project and save it in the database
        project = models.Project(
            name=name,
            url=url,
            analysis=json.dumps(analysis),
            status="analyzed"
        )
        db.session.add(project)
        db.session.commit()
        
        # Redirect to the funnel editor with the project ID
        return redirect(url_for('funnel_editor', project_id=project.id))
    
    except Exception as e:
        logger.error(f"Error analyzing URL: {str(e)}")
        flash(f"Error analyzing URL: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/funnel_editor/<int:project_id>')
def funnel_editor(project_id):
    """Funnel editor page for a specific project"""
    project = models.Project.query.get_or_404(project_id)
    analysis = json.loads(project.analysis)
    return render_template('funnel_editor.html', project=project, analysis=analysis)

@app.route('/generate_funnel/<int:project_id>', methods=['POST'])
def create_funnel(project_id):
    """Generate a funnel based on a project"""
    project = models.Project.query.get_or_404(project_id)
    
    try:
        # Get customization parameters from form
        customizations = {
            'brand_name': request.form.get('brand_name'),
            'unique_angle': request.form.get('unique_angle'),
            'target_audience': request.form.get('target_audience'),
            'num_upsells': int(request.form.get('num_upsells', 10)),
            'num_downsells': int(request.form.get('num_downsells', 10))
        }
        
        # Generate funnel content using AI
        analysis = json.loads(project.analysis)
        funnel_data = generate_funnel(analysis, customizations)
        
        # Save funnel to the project
        project.funnel_data = json.dumps(funnel_data)
        project.status = "funnel_generated"
        db.session.commit()
        
        # Redirect to email sequence generator
        return redirect(url_for('email_sequence', project_id=project.id))
    
    except Exception as e:
        logger.error(f"Error generating funnel: {str(e)}")
        flash(f"Error generating funnel: {str(e)}", "danger")
        return redirect(url_for('funnel_editor', project_id=project_id))

@app.route('/email_sequence/<int:project_id>')
def email_sequence(project_id):
    """Email sequence generator page"""
    project = models.Project.query.get_or_404(project_id)
    funnel_data = json.loads(project.funnel_data) if project.funnel_data else None
    return render_template('email_sequence.html', project=project, funnel_data=funnel_data)

@app.route('/generate_emails/<int:project_id>', methods=['POST'])
def create_email_sequence(project_id):
    """Generate email sequence for a project"""
    project = models.Project.query.get_or_404(project_id)
    
    try:
        # Get email sequence parameters
        params = {
            'num_emails': int(request.form.get('num_emails', 10)),
            'sequence_type': request.form.get('sequence_type', 'sales'),
            'email_style': request.form.get('email_style', 'conversational')
        }
        
        # Generate email sequence using AI
        funnel_data = json.loads(project.funnel_data)
        email_sequence = generate_email_sequence(funnel_data, params)
        
        # Save email sequence to the project
        project.email_sequence = json.dumps(email_sequence)
        project.status = "completed"
        db.session.commit()
        
        # Redirect to export page
        return redirect(url_for('export', project_id=project.id))
    
    except Exception as e:
        logger.error(f"Error generating email sequence: {str(e)}")
        flash(f"Error generating email sequence: {str(e)}", "danger")
        return redirect(url_for('email_sequence', project_id=project_id))

@app.route('/export/<int:project_id>')
def export(project_id):
    """Export page for the generated funnel and emails"""
    project = models.Project.query.get_or_404(project_id)
    funnel_data = json.loads(project.funnel_data) if project.funnel_data else None
    email_sequence = json.loads(project.email_sequence) if project.email_sequence else None
    return render_template('export.html', project=project, funnel_data=funnel_data, email_sequence=email_sequence)

@app.route('/download/<int:project_id>', methods=['POST'])
def download_project(project_id):
    """Create and download a zip file of the project"""
    from funnel_generator import create_zip_export
    project = models.Project.query.get_or_404(project_id)
    
    try:
        # Create a zip file with the entire project
        zip_path = create_zip_export(project)
        
        # Return the zip file
        # This will be implemented in the funnel_generator.py file
        return jsonify({'success': True, 'download_url': url_for('static', filename=f'exports/{project.id}.zip')})
    
    except Exception as e:
        logger.error(f"Error creating download: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    """Delete a project"""
    project = models.Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash("Project deleted successfully", "success")
    return redirect(url_for('dashboard'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error="Server error. Please try again later."), 500
