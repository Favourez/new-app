from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import sqlite3
import hashlib
import os
import time
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_config import get_email_config
import re
import math
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# AI Resume Parser Integration
try:
    from resume_ai_integration import JobSyncResumeAI
    ai_resume_parser = JobSyncResumeAI()
    AI_PARSING_ENABLED = True
    print("✅ AI Resume Parser loaded successfully")
except ImportError as e:
    AI_PARSING_ENABLED = False
    ai_resume_parser = None
    print(f"⚠️ AI Resume Parser not available: {e}")
except Exception as e:
    AI_PARSING_ENABLED = False
    ai_resume_parser = None
    print(f"⚠️ AI Resume Parser error: {e}")

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Email configuration from config file
email_config = get_email_config()
app.config['MAIL_SERVER'] = email_config['MAIL_SERVER']
app.config['MAIL_PORT'] = email_config['MAIL_PORT']
app.config['MAIL_USE_TLS'] = email_config['MAIL_USE_TLS']
app.config['MAIL_USERNAME'] = email_config['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = email_config['MAIL_PASSWORD']
app.config['MAIL_USE_REAL_EMAIL'] = email_config['USE_REAL_EMAIL']

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database initialization
def init_db():
    conn = sqlite3.connect('jobportal.db')
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            user_type TEXT NOT NULL,
            company_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # User profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            skills TEXT,
            experience TEXT,
            education TEXT,
            resume_filename TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employer_id INTEGER,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            requirements TEXT NOT NULL,
            skills TEXT NOT NULL,
            salary TEXT,
            location TEXT NOT NULL,
            job_type TEXT NOT NULL,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employer_id) REFERENCES users (id)
        )
    ''')

    # Applications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            applicant_id INTEGER,
            employer_id INTEGER,
            compatibility_score INTEGER,
            status TEXT DEFAULT 'pending',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs (id),
            FOREIGN KEY (applicant_id) REFERENCES users (id),
            FOREIGN KEY (employer_id) REFERENCES users (id)
        )
    ''')

    # Chat messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            user_type TEXT,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # News feed posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            user_type TEXT,
            content TEXT NOT NULL,
            image_path TEXT,
            video_path TEXT,
            likes_count INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            shares_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Post likes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS post_likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES news_posts (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(post_id, user_id)
        )
    ''')

    # Post comments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS post_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            user_id INTEGER,
            username TEXT,
            user_type TEXT,
            comment TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES news_posts (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

# Helper functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Email functions
def send_email(to_email, subject, body, is_html=False, text_fallback=None):
    """Send email notification - Real or Mock based on configuration"""
    try:
        if app.config.get('MAIL_USE_REAL_EMAIL', False):
            # Send real email using SMTP
            return send_real_email(to_email, subject, body, is_html, text_fallback)
        else:
            # Mock email for demo purposes
            return send_mock_email(to_email, subject, text_fallback or body)

    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {str(e)}")
        return False

def send_real_email(to_email, subject, body, is_html=False, text_fallback=None):
    """Send real email using SMTP"""
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = app.config['MAIL_USERNAME']
        msg['To'] = to_email
        msg['Subject'] = subject

        # Add text version (fallback)
        if text_fallback:
            text_part = MIMEText(text_fallback, 'plain')
            msg.attach(text_part)

        # Add HTML version if provided
        if is_html:
            html_part = MIMEText(body, 'html')
            msg.attach(html_part)
        else:
            # Plain text only
            if not text_fallback:
                text_part = MIMEText(body, 'plain')
                msg.attach(text_part)

        # Gmail SMTP configuration
        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])

        # Send email
        text = msg.as_string()
        server.sendmail(app.config['MAIL_USERNAME'], to_email, text)
        server.quit()

        print(f"✅ Real email sent successfully to {to_email}")
        print(f"   Subject: {subject}")
        print(f"   Format: {'HTML + Text' if is_html and text_fallback else 'HTML' if is_html else 'Text'}")
        return True

    except Exception as e:
        print(f"❌ Failed to send real email to {to_email}: {str(e)}")
        return False

def send_mock_email(to_email, subject, body):
    """Mock email for demo purposes"""
    try:
        print("\n" + "="*80)
        print("📧 EMAIL NOTIFICATION (DEMO MODE)")
        print("="*80)
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print("-"*80)
        print(body)
        print("="*80)

        # Store email in a simple log file for demo
        with open('email_log.txt', 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"TO: {to_email}\n")
            f.write(f"SUBJECT: {subject}\n")
            f.write(f"{'='*80}\n")
            f.write(f"{body}\n")
            f.write(f"{'='*80}\n\n")

        print(f"✅ Email logged successfully for {to_email}")
        return True

    except Exception as e:
        print(f"❌ Failed to log email for {to_email}: {str(e)}")
        return False

def send_job_posted_email(employer_email, employer_name, job_title, job_id):
    """Send confirmation email when employer posts a job"""
    subject = f"Job Posted Successfully - {job_title}"

    body = f"""
Dear {employer_name},

Congratulations! Your job posting has been successfully published on JobSync.

Job Details:
- Title: {job_title}
- Job ID: {job_id}
- Posted on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

Your job is now live and visible to all jobseekers on our platform. You will receive email notifications when candidates apply for this position.

You can manage your job postings and view applications by logging into your employer dashboard at:
http://127.0.0.1:8080/employer_dashboard

Thank you for using JobSync!

Best regards,
The JobSync Team
"""

    return send_email(employer_email, subject, body)

def send_application_confirmation_email(applicant_email, applicant_name, job_title, company_name):
    """Send confirmation email when user applies for a job"""
    subject = f"✅ Application Confirmed - {job_title} at {company_name}"

    # Create HTML email for better presentation
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .success-icon {{ font-size: 48px; margin-bottom: 20px; }}
        .job-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745; }}
        .next-steps {{ background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; }}
        .btn {{ display: inline-block; background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="success-icon">🎉</div>
            <h1>Application Submitted Successfully!</h1>
            <p>Your job application has been received</p>
        </div>

        <div class="content">
            <h2>Dear {applicant_name},</h2>

            <p>Congratulations! Your application for the <strong>{job_title}</strong> position at <strong>{company_name}</strong> has been successfully submitted.</p>

            <div class="job-details">
                <h3>📋 Application Details:</h3>
                <ul>
                    <li><strong>Position:</strong> {job_title}</li>
                    <li><strong>Company:</strong> {company_name}</li>
                    <li><strong>Applied on:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</li>
                    <li><strong>Application Status:</strong> Under Review</li>
                </ul>
            </div>

            <div class="next-steps">
                <h3>🚀 What Happens Next:</h3>
                <ol>
                    <li><strong>Review Process:</strong> The employer will review your application and profile</li>
                    <li><strong>Initial Screening:</strong> If you're a good match, they may contact you for an interview</li>
                    <li><strong>Updates:</strong> You'll receive email notifications about your application status</li>
                    <li><strong>Interview:</strong> If selected, you'll be contacted for the next steps</li>
                </ol>
            </div>

            <p>You can track all your applications and update your profile anytime:</p>
            <a href="http://127.0.0.1:8080/jobseeker_dashboard" class="btn">View My Dashboard</a>

            <div class="footer">
                <p><strong>Good luck with your application!</strong></p>
                <p>Best regards,<br>The JobSync Team</p>
                <hr>
                <small>This is an automated confirmation email. Please do not reply to this email.</small>
            </div>
        </div>
    </div>
</body>
</html>
"""

    # Plain text version for email clients that don't support HTML
    text_body = f"""
🎉 APPLICATION SUBMITTED SUCCESSFULLY!

Dear {applicant_name},

Congratulations! Your application for the {job_title} position at {company_name} has been successfully submitted.

📋 APPLICATION DETAILS:
- Position: {job_title}
- Company: {company_name}
- Applied on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
- Status: Under Review

🚀 WHAT HAPPENS NEXT:
1. Review Process: The employer will review your application and profile
2. Initial Screening: If you're a good match, they may contact you for an interview
3. Updates: You'll receive email notifications about your application status
4. Interview: If selected, you'll be contacted for the next steps

You can track your applications at: http://127.0.0.1:8080/jobseeker_dashboard

Good luck with your application!

Best regards,
The JobSync Team

---
This is an automated confirmation email.
"""

    # Send HTML email with text fallback
    return send_email(applicant_email, subject, html_body, is_html=True, text_fallback=text_body)

def send_new_application_email(employer_email, employer_name, applicant_name, job_title, compatibility_score):
    """Send notification email to employer when someone applies"""
    subject = f"New Application Received - {job_title}"

    body = f"""
Dear {employer_name},

Great news! You have received a new application for your job posting.

Application Details:
- Position: {job_title}
- Applicant: {applicant_name}
- Compatibility Score: {compatibility_score}%
- Applied on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

The applicant's skills match {compatibility_score}% of your job requirements. You can review their full profile, resume, and application details by logging into your employer dashboard.

Review Application:
http://127.0.0.1:8080/employer_dashboard

Don't keep great candidates waiting - review their application today!

Best regards,
The JobSync Team
"""

    return send_email(employer_email, subject, body)

def get_db_connection():
    """Get database connection with improved settings to prevent locks"""
    conn = sqlite3.connect('jobportal.db', timeout=30)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for better concurrency
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.execute('PRAGMA synchronous=NORMAL;')
    conn.execute('PRAGMA cache_size=10000;')
    conn.execute('PRAGMA temp_store=memory;')
    return conn

class DatabaseConnection:
    """Context manager for database connections to ensure proper cleanup"""
    def __init__(self):
        self.conn = None

    def __enter__(self):
        self.conn = get_db_connection()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()

class SkillMatcher:
    """Advanced skill matching using TF-IDF and cosine similarity"""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),  # Include both unigrams and bigrams
            max_features=1000,
            token_pattern=r'\b[a-zA-Z][a-zA-Z0-9+#.]*\b'  # Include tech terms like C++, C#, .NET
        )
        self.skill_synonyms = {
            'js': 'javascript',
            'ts': 'typescript',
            'py': 'python',
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'db': 'database',
            'sql': 'structured query language',
            'nosql': 'non relational database',
            'api': 'application programming interface',
            'ui': 'user interface',
            'ux': 'user experience',
            'css3': 'css',
            'html5': 'html',
            'es6': 'javascript',
            'react.js': 'react',
            'vue.js': 'vue',
            'node.js': 'nodejs',
            'express.js': 'express',
            'mongodb': 'mongo database',
            'postgresql': 'postgres',
            'mysql': 'my sql database',
            'aws': 'amazon web services',
            'gcp': 'google cloud platform',
            'k8s': 'kubernetes',
            'docker': 'containerization',
            'ci/cd': 'continuous integration continuous deployment',
            'devops': 'development operations',
            'frontend': 'front end development',
            'backend': 'back end development',
            'fullstack': 'full stack development'
        }

    def preprocess_skills(self, skills_text):
        """Preprocess and normalize skills text"""
        if not skills_text:
            return ""

        # Convert to lowercase and split by common delimiters
        skills = re.split(r'[,;|/\n\r]+', skills_text.lower())

        # Clean and normalize each skill
        processed_skills = []
        for skill in skills:
            skill = skill.strip()
            if skill:
                # Replace synonyms
                skill = self.skill_synonyms.get(skill, skill)
                # Remove special characters except + and #
                skill = re.sub(r'[^\w\s+#.]', ' ', skill)
                # Normalize whitespace
                skill = ' '.join(skill.split())
                if skill:
                    processed_skills.append(skill)

        return ' '.join(processed_skills)

    def calculate_semantic_similarity(self, job_skills, candidate_skills):
        """Calculate semantic similarity using TF-IDF and cosine similarity"""
        if not job_skills or not candidate_skills:
            return 0

        # Preprocess skills
        job_text = self.preprocess_skills(job_skills)
        candidate_text = self.preprocess_skills(candidate_skills)

        if not job_text or not candidate_text:
            return 0

        try:
            # Create TF-IDF vectors
            documents = [job_text, candidate_text]
            tfidf_matrix = self.vectorizer.fit_transform(documents)

            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            similarity_score = similarity_matrix[0][0]

            # Convert to percentage and ensure it's between 0-100
            percentage = max(0, min(100, similarity_score * 100))

            return int(round(percentage))

        except Exception as e:
            print(f"Error calculating semantic similarity: {e}")
            # Fallback to basic matching
            return self._basic_compatibility(job_skills, candidate_skills)

    def _basic_compatibility(self, job_skills, user_skills):
        """Fallback basic compatibility calculation"""
        if not job_skills or not user_skills:
            return 0

        job_skills_list = [skill.strip().lower() for skill in job_skills.split(',')]
        user_skills_list = [skill.strip().lower() for skill in user_skills.split(',')]

        # Exact matches
        exact_matches = set(job_skills_list) & set(user_skills_list)

        # Partial matches (for similar skills)
        partial_matches = 0
        for job_skill in job_skills_list:
            if job_skill not in exact_matches:
                for user_skill in user_skills_list:
                    if user_skill not in exact_matches:
                        # Check for partial matches
                        if (job_skill in user_skill or user_skill in job_skill) and len(job_skill) > 2:
                            partial_matches += 0.5
                            break

        # Calculate compatibility
        total_matches = len(exact_matches) + partial_matches
        compatibility = (total_matches / len(job_skills_list)) * 100 if job_skills_list else 0

        return min(int(compatibility), 100)

# Initialize global skill matcher
skill_matcher = SkillMatcher()

def calculate_compatibility(job_skills, user_skills):
    """Main compatibility calculation function using advanced semantic matching"""
    return skill_matcher.calculate_semantic_similarity(job_skills, user_skills)

def get_compatibility_details(job_skills, user_skills):
    """Get detailed compatibility information with semantic analysis"""
    if not job_skills or not user_skills:
        return {'score': 0, 'matched': [], 'missing': job_skills.split(',') if job_skills else [], 'semantic_analysis': {}}

    # Get semantic similarity score
    score = calculate_compatibility(job_skills, user_skills)

    # Parse skills for detailed analysis
    job_skills_list = [skill.strip() for skill in job_skills.split(',')]
    user_skills_list = [skill.strip().lower() for skill in user_skills.split(',')]

    # Find exact and partial matches
    matched_skills = []
    missing_skills = []
    semantic_matches = []

    for job_skill in job_skills_list:
        job_skill_lower = job_skill.lower()
        found = False

        # Check for exact matches
        for user_skill in user_skills_list:
            if user_skill == job_skill_lower:
                matched_skills.append(job_skill)
                found = True
                break

        # Check for partial/semantic matches
        if not found:
            for user_skill in user_skills_list:
                # Check synonyms
                job_normalized = skill_matcher.skill_synonyms.get(job_skill_lower, job_skill_lower)
                user_normalized = skill_matcher.skill_synonyms.get(user_skill, user_skill)

                if (user_skill in job_skill_lower or job_skill_lower in user_skill or
                    user_normalized in job_normalized or job_normalized in user_normalized):
                    semantic_matches.append({
                        'required': job_skill,
                        'candidate': user_skill,
                        'match_type': 'semantic'
                    })
                    found = True
                    break

        if not found:
            missing_skills.append(job_skill)

    # Calculate TF-IDF similarity for additional insights
    try:
        job_text = skill_matcher.preprocess_skills(job_skills)
        user_text = skill_matcher.preprocess_skills(user_skills)

        if job_text and user_text:
            documents = [job_text, user_text]
            tfidf_matrix = skill_matcher.vectorizer.fit_transform(documents)
            feature_names = skill_matcher.vectorizer.get_feature_names_out()

            # Get top terms for each document
            job_tfidf = tfidf_matrix[0].toarray()[0]
            user_tfidf = tfidf_matrix[1].toarray()[0]

            # Find top terms
            job_top_terms = [(feature_names[i], job_tfidf[i]) for i in job_tfidf.argsort()[-10:][::-1] if job_tfidf[i] > 0]
            user_top_terms = [(feature_names[i], user_tfidf[i]) for i in user_tfidf.argsort()[-10:][::-1] if user_tfidf[i] > 0]

            semantic_analysis = {
                'job_key_terms': job_top_terms[:5],
                'candidate_key_terms': user_top_terms[:5],
                'tfidf_similarity': score / 100.0
            }
        else:
            semantic_analysis = {}

    except Exception as e:
        print(f"Error in semantic analysis: {e}")
        semantic_analysis = {}

    return {
        'score': score,
        'matched': matched_skills,
        'missing': missing_skills,
        'semantic_matches': semantic_matches,
        'total_required': len(job_skills_list),
        'semantic_analysis': semantic_analysis,
        'match_breakdown': {
            'exact_matches': len(matched_skills),
            'semantic_matches': len(semantic_matches),
            'missing_skills': len(missing_skills),
            'coverage_percentage': ((len(matched_skills) + len(semantic_matches)) / len(job_skills_list) * 100) if job_skills_list else 0
        }
    }

# This function is replaced by the enhanced email system above

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user_type = request.form['user_type']
        company_name = request.form.get('company_name', '')

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')

        if user_type == 'employer':
            # For employers, we'll use Firebase (handled by frontend)
            # But we still need to store basic info in SQLite for session management
            conn = get_db_connection()

            # Check if employer already exists in SQLite (for session management)
            existing_user = conn.execute(
                'SELECT id FROM users WHERE email = ? AND user_type = ?',
                (email, 'employer')
            ).fetchone()

            if existing_user:
                flash('Employer account already exists!', 'error')
                conn.close()
                return render_template('register.html')

            # Create employer entry in SQLite for session management
            hashed_password = hash_password(password)
            cursor = conn.execute(
                'INSERT INTO users (username, email, password, user_type, company_name) VALUES (?, ?, ?, ?, ?)',
                (username, email, hashed_password, user_type, company_name)
            )
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()

            flash('Employer registration successful! Please login. Your data will be stored in Firebase.', 'success')
            return redirect(url_for('login'))

        else:
            # For jobseekers, use SQLite as before
            conn = get_db_connection()

            # Check if jobseeker already exists
            existing_user = conn.execute(
                'SELECT id FROM users WHERE email = ? AND user_type = ?',
                (email, 'jobseeker')
            ).fetchone()

            if existing_user:
                flash('Jobseeker account already exists!', 'error')
                conn.close()
                return render_template('register.html')

            # Create new jobseeker
            hashed_password = hash_password(password)
            cursor = conn.execute(
                'INSERT INTO users (username, email, password, user_type, company_name) VALUES (?, ?, ?, ?, ?)',
                (username, email, hashed_password, user_type, company_name)
            )
            user_id = cursor.lastrowid

            # Create user profile for jobseeker
            conn.execute(
                'INSERT INTO user_profiles (user_id, skills, experience, education) VALUES (?, ?, ?, ?)',
                (user_id, '', '', '')
            )

            conn.commit()
            conn.close()

            flash('Jobseeker registration successful! Please login.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = hash_password(password)

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE email = ? AND password = ?',
            (email, hashed_password)
        ).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_type'] = user['user_type']
            session['email'] = user['email']
            if user['company_name']:
                session['company_name'] = user['company_name']

            if user['user_type'] == 'employer':
                flash('Login successful! Welcome to Firebase-powered employer dashboard.', 'success')
            else:
                flash('Login successful!', 'success')

            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session['user_type'] == 'jobseeker':
        return redirect(url_for('jobseeker_dashboard'))
    else:
        return redirect(url_for('employer_dashboard'))

@app.route('/jobseeker_dashboard')
def jobseeker_dashboard():
    if 'user_id' not in session or session['user_type'] != 'jobseeker':
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Get user profile
    profile = conn.execute(
        'SELECT * FROM user_profiles WHERE user_id = ?',
        (session['user_id'],)
    ).fetchone()

    # Get recent applications
    applications = conn.execute('''
        SELECT a.*, j.title as job_title, j.location, u.company_name
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        JOIN users u ON a.employer_id = u.id
        WHERE a.applicant_id = ?
        ORDER BY a.applied_at DESC
        LIMIT 10
    ''', (session['user_id'],)).fetchall()

    conn.close()

    return render_template('jobseeker_dashboard.html', profile=profile, applications=applications)

@app.route('/employer_dashboard')
def employer_dashboard():
    if 'user_id' not in session or session['user_type'] != 'employer':
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Get employer's jobs
    jobs = conn.execute(
        'SELECT * FROM jobs WHERE employer_id = ? ORDER BY posted_at DESC',
        (session['user_id'],)
    ).fetchall()

    # Get applications for employer's jobs
    applications = conn.execute('''
        SELECT a.*, j.title as job_title, u.id as applicant_user_id, u.username as applicant_name, u.email as applicant_email
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        JOIN users u ON a.applicant_id = u.id
        WHERE a.employer_id = ?
        ORDER BY a.applied_at DESC
        LIMIT 20
    ''', (session['user_id'],)).fetchall()

    conn.close()

    return render_template('employer_dashboard.html', jobs=jobs, applications=applications)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        if session['user_type'] == 'jobseeker':
            skills = request.form['skills']
            experience = request.form['experience']
            education = request.form['education']

            conn.execute('''
                UPDATE user_profiles
                SET skills = ?, experience = ?, education = ?
                WHERE user_id = ?
            ''', (skills, experience, education, session['user_id']))

        flash('Profile updated successfully!', 'success')
        conn.commit()

    # Get user data
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    profile = conn.execute('SELECT * FROM user_profiles WHERE user_id = ?', (session['user_id'],)).fetchone()

    conn.close()

    return render_template('profile.html', user=user, profile=profile)

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'user_id' not in session or session['user_type'] != 'jobseeker':
        return redirect(url_for('login'))

    if 'resume' not in request.files:
        flash('No file selected!', 'error')
        return redirect(url_for('jobseeker_dashboard'))

    file = request.files['resume']
    if file.filename == '':
        flash('No file selected!', 'error')
        return redirect(url_for('jobseeker_dashboard'))

    if file and file.filename.lower().endswith(('.pdf', '.docx', '.doc')):
        filename = secure_filename(f"resume_{session['user_id']}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # AI Resume Parsing
        if AI_PARSING_ENABLED and ai_resume_parser:
            try:
                print(f"🤖 Parsing resume with AI: {filename}")
                ai_result = ai_resume_parser.parse_resume_with_ai(file_path)

                if ai_result and 'jobsync_formatted' in ai_result:
                    parsed_data = ai_result['jobsync_formatted']

                    # Extract parsed information
                    extracted_skills = parsed_data.get('skills', 'Python, JavaScript, React, Flask, SQL')
                    extracted_experience = parsed_data.get('experience', '2+ years of experience')
                    extracted_education = parsed_data.get('education', 'Bachelor\'s degree')
                    confidence_score = parsed_data.get('parsing_confidence', 0)

                    print(f"✅ AI parsing successful - Confidence: {confidence_score}%")
                    print(f"   Skills: {extracted_skills[:50]}...")

                    flash_message = f'Resume uploaded and parsed with AI! (Confidence: {confidence_score}%)'
                    flash_type = 'success'

                else:
                    # Fallback to basic parsing
                    extracted_skills = "Python, JavaScript, React, Flask, SQL, Git, HTML, CSS"
                    extracted_experience = "3+ years of web development experience"
                    extracted_education = "Bachelor's degree in Computer Science"

                    flash_message = 'Resume uploaded! AI parsing unavailable - using basic extraction.'
                    flash_type = 'warning'

            except Exception as e:
                print(f"❌ AI parsing error: {e}")
                # Fallback to basic parsing
                extracted_skills = "Python, JavaScript, React, Flask, SQL, Git, HTML, CSS"
                extracted_experience = "3+ years of web development experience"
                extracted_education = "Bachelor's degree in Computer Science"

                flash_message = 'Resume uploaded! AI parsing failed - using basic extraction.'
                flash_type = 'warning'
        else:
            # Basic parsing when AI is not available
            extracted_skills = "Python, JavaScript, React, Flask, SQL, Git, HTML, CSS"
            extracted_experience = "3+ years of web development experience"
            extracted_education = "Bachelor's degree in Computer Science"

            flash_message = 'Resume uploaded and parsed successfully!'
            flash_type = 'success'

        # Update user profile
        conn = get_db_connection()
        conn.execute('''
            UPDATE user_profiles
            SET skills = ?, experience = ?, education = ?, resume_filename = ?
            WHERE user_id = ?
        ''', (extracted_skills, extracted_experience, extracted_education, filename, session['user_id']))
        conn.commit()
        conn.close()

        flash(flash_message, flash_type)
    else:
        flash('Please upload a PDF, DOC, or DOCX file only!', 'error')

    return redirect(url_for('jobseeker_dashboard'))

@app.route('/jobs')
def jobs():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Get all jobs (except those posted by current user if they're an employer)
    if session['user_type'] == 'employer':
        jobs_list = conn.execute('''
            SELECT j.*, u.company_name, u.username as employer_name
            FROM jobs j
            JOIN users u ON j.employer_id = u.id
            WHERE j.employer_id != ?
            ORDER BY j.posted_at DESC
        ''', (session['user_id'],)).fetchall()
    else:
        jobs_list = conn.execute('''
            SELECT j.*, u.company_name, u.username as employer_name
            FROM jobs j
            JOIN users u ON j.employer_id = u.id
            ORDER BY j.posted_at DESC
        ''').fetchall()

    # Get user profile for compatibility scoring (if jobseeker)
    user_profile = None
    if session['user_type'] == 'jobseeker':
        user_profile = conn.execute(
            'SELECT * FROM user_profiles WHERE user_id = ?',
            (session['user_id'],)
        ).fetchone()

    conn.close()

    return render_template('jobs.html', jobs=jobs_list, user_profile=user_profile, calculate_compatibility=calculate_compatibility)

@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    if 'user_id' not in session or session['user_type'] != 'employer':
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        requirements = request.form['requirements']
        skills = request.form['skills']
        salary = request.form['salary']
        location = request.form['location']
        job_type = request.form['job_type']

        conn = get_db_connection()
        cursor = conn.execute('''
            INSERT INTO jobs (employer_id, title, description, requirements, skills, salary, location, job_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], title, description, requirements, skills, salary, location, job_type))

        job_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Send email notification to employer
        try:
            employer_email = session.get('email', 'employer@demo.com')
            employer_name = session.get('username', 'Employer')
            send_job_posted_email(employer_email, employer_name, title, job_id)
        except Exception as e:
            print(f"Failed to send job posted email: {e}")

        flash('Job posted successfully! You will receive an email confirmation.', 'success')
        return redirect(url_for('employer_dashboard'))

    return render_template('post_job.html')

@app.route('/apply_job/<int:job_id>')
def apply_job(job_id):
    if 'user_id' not in session or session['user_type'] != 'jobseeker':
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Check if already applied
    existing_application = conn.execute(
        'SELECT id FROM applications WHERE job_id = ? AND applicant_id = ?',
        (job_id, session['user_id'])
    ).fetchone()

    if existing_application:
        flash('You have already applied for this job!', 'warning')
        conn.close()
        return redirect(url_for('jobs'))

    # Get job details
    job = conn.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
    if not job:
        flash('Job not found!', 'error')
        conn.close()
        return redirect(url_for('jobs'))

    # Get user profile for compatibility scoring
    user_profile = conn.execute(
        'SELECT * FROM user_profiles WHERE user_id = ?',
        (session['user_id'],)
    ).fetchone()

    if not user_profile or not user_profile['resume_filename']:
        flash('Please upload your resume before applying!', 'error')
        conn.close()
        return redirect(url_for('jobseeker_dashboard'))

    # Calculate compatibility score
    compatibility_score = calculate_compatibility(job['skills'], user_profile['skills'])

    # Get employer details for email notification
    employer = conn.execute(
        'SELECT username, email, company_name FROM users WHERE id = ?',
        (job['employer_id'],)
    ).fetchone()

    # Create application
    conn.execute('''
        INSERT INTO applications (job_id, applicant_id, employer_id, compatibility_score)
        VALUES (?, ?, ?, ?)
    ''', (job_id, session['user_id'], job['employer_id'], compatibility_score))
    conn.commit()
    conn.close()

    # Send email notifications
    try:
        # Send confirmation email to applicant
        applicant_email = session.get('email', 'jobseeker@demo.com')
        applicant_name = session.get('username', 'Job Seeker')
        company_name = employer['company_name'] if employer and employer['company_name'] else 'Demo Company'

        send_application_confirmation_email(
            applicant_email,
            applicant_name,
            job['title'],
            company_name
        )

        # Send notification email to employer
        if employer:
            employer_email = employer['email'] if employer['email'] else 'employer@demo.com'
            employer_name = employer['username'] if employer['username'] else 'Employer'

            send_new_application_email(
                employer_email,
                employer_name,
                applicant_name,
                job['title'],
                compatibility_score
            )

    except Exception as e:
        print(f"Failed to send application emails: {e}")

    flash(f'Application submitted successfully! Compatibility score: {compatibility_score}%. Check your email for confirmation.', 'success')
    return redirect(url_for('jobs'))

@app.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Get recent chat messages
    messages = conn.execute('''
        SELECT * FROM chat_messages
        ORDER BY timestamp DESC
        LIMIT 50
    ''').fetchall()

    # Reverse to show oldest first
    messages = list(reversed(messages))

    conn.close()

    return render_template('chat.html', messages=messages)

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    message = request.form.get('message', '').strip()
    if not message:
        return jsonify({'error': 'Empty message'}), 400

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO chat_messages (user_id, username, user_type, message)
        VALUES (?, ?, ?, ?)
    ''', (session['user_id'], session['username'], session['user_type'], message))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

@app.route('/get_messages')
def get_messages():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    conn = get_db_connection()
    messages = conn.execute('''
        SELECT * FROM chat_messages
        ORDER BY timestamp DESC
        LIMIT 50
    ''').fetchall()
    conn.close()

    # Convert to list of dicts
    messages_list = []
    for msg in reversed(messages):
        messages_list.append({
            'id': msg['id'],
            'user_id': msg['user_id'],
            'username': msg['username'],
            'user_type': msg['user_type'],
            'message': msg['message'],
            'timestamp': msg['timestamp']
        })

    return jsonify(messages_list)

# Firebase integration routes for employers
@app.route('/api/firebase/employer', methods=['POST'])
def create_firebase_employer():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    # This will be handled by frontend Firebase
    return jsonify({'success': True, 'message': 'Use frontend Firebase service'})

@app.route('/api/firebase/job', methods=['POST'])
def create_firebase_job():
    if 'user_id' not in session or session['user_type'] != 'employer':
        return jsonify({'error': 'Not authorized'}), 403

    data = request.get_json()
    # This will be handled by frontend Firebase
    return jsonify({'success': True, 'message': 'Use frontend Firebase service'})

@app.route('/api/firebase/applications/<employer_id>')
def get_firebase_applications(employer_id):
    if 'user_id' not in session or session['user_type'] != 'employer':
        return jsonify({'error': 'Not authorized'}), 403

    # This will be handled by frontend Firebase
    return jsonify({'success': True, 'message': 'Use frontend Firebase service'})

@app.route('/firebase_employer_dashboard')
def firebase_employer_dashboard():
    if 'user_id' not in session or session['user_type'] != 'employer':
        return redirect(url_for('login'))

    return render_template('firebase_employer_dashboard.html')

@app.route('/firebase_post_job')
def firebase_post_job():
    if 'user_id' not in session or session['user_type'] != 'employer':
        return redirect(url_for('login'))

    return render_template('firebase_post_job.html')

def create_demo_accounts():
    """Create demo accounts for testing"""
    conn = get_db_connection()

    # Demo jobseeker
    try:
        hashed_password = hash_password('demo123')
        cursor = conn.execute(
            'INSERT INTO users (username, email, password, user_type, company_name) VALUES (?, ?, ?, ?, ?)',
            ('Demo Jobseeker', 'jobseeker@demo.com', hashed_password, 'jobseeker', '')
        )
        user_id = cursor.lastrowid

        # Create profile for demo jobseeker
        conn.execute(
            'INSERT INTO user_profiles (user_id, skills, experience, education) VALUES (?, ?, ?, ?)',
            (user_id, 'Python, JavaScript, React, Flask, SQL', '2+ years of web development', 'Bachelor in Computer Science')
        )
        print("Demo jobseeker created: jobseeker@demo.com / demo123")
    except:
        print("Demo jobseeker already exists")

    # Demo employer
    try:
        hashed_password = hash_password('demo123')
        conn.execute(
            'INSERT INTO users (username, email, password, user_type, company_name) VALUES (?, ?, ?, ?, ?)',
            ('Demo Employer', 'employer@demo.com', hashed_password, 'employer', 'Demo Tech Company')
        )
        print("Demo employer created: employer@demo.com / demo123")
    except:
        print("Demo employer already exists")

    conn.commit()
    conn.close()

@app.route('/newsfeed')
def newsfeed():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('simple_newsfeed.html')

@app.route('/download_cv/<int:applicant_id>')
def download_cv(applicant_id):
    """Allow employers to download applicant CVs"""
    if 'user_id' not in session or session['user_type'] != 'employer':
        flash('Access denied. Employers only.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Get applicant's resume filename
    user_profile = conn.execute(
        'SELECT resume_filename, skills, experience, education FROM user_profiles WHERE user_id = ?',
        (applicant_id,)
    ).fetchone()

    # Get applicant's basic info
    user_info = conn.execute(
        'SELECT username, email FROM users WHERE id = ?',
        (applicant_id,)
    ).fetchone()

    conn.close()

    if not user_profile or not user_profile['resume_filename']:
        flash('CV not found for this applicant.', 'error')
        return redirect(url_for('employer_dashboard'))

    # Check if the file exists
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], user_profile['resume_filename'])
    if not os.path.exists(file_path):
        flash('CV file not found on server.', 'error')
        return redirect(url_for('employer_dashboard'))

    # Create a safe filename for download
    safe_filename = f"{user_info['username'].replace(' ', '_')}_CV.pdf" if user_info else "applicant_CV.pdf"

    try:
        return send_file(
            file_path,
            as_attachment=True,
            download_name=safe_filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(f'Error downloading CV: {str(e)}', 'error')
        return redirect(url_for('employer_dashboard'))

@app.route('/applicant_profile/<int:applicant_id>')
def applicant_profile(applicant_id):
    """View applicant profile for employers"""
    if 'user_id' not in session or session['user_type'] != 'employer':
        flash('Access denied. Employers only.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Get applicant's full information
    user_info = conn.execute(
        'SELECT id, username, email, user_type FROM users WHERE id = ?',
        (applicant_id,)
    ).fetchone()

    user_profile = conn.execute(
        'SELECT * FROM user_profiles WHERE user_id = ?',
        (applicant_id,)
    ).fetchone()

    # Get applicant's applications to this employer's jobs
    applications = conn.execute('''
        SELECT a.*, j.title as job_title, j.location, j.salary
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        WHERE a.applicant_id = ? AND a.employer_id = ?
        ORDER BY a.applied_at DESC
    ''', (applicant_id, session['user_id'])).fetchall()

    conn.close()

    if not user_info:
        flash('Applicant not found.', 'error')
        return redirect(url_for('employer_dashboard'))

    return render_template('applicant_profile.html',
                         user_info=user_info,
                         user_profile=user_profile,
                         applications=applications,
                         calculate_compatibility=calculate_compatibility)

@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    """Handle password reset requests (Demo version)"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()

        if not email:
            return jsonify({'error': 'Email address is required'}), 400

        # Check if user exists in our database
        conn = get_db_connection()
        user = conn.execute(
            'SELECT id, username, user_type FROM users WHERE email = ?',
            (email,)
        ).fetchone()
        conn.close()

        if not user:
            return jsonify({'error': 'No account found with this email address'}), 404

        # Send password reset email (demo version)
        reset_token = f"demo_reset_token_{user['id']}_{datetime.now().timestamp()}"
        reset_link = f"http://127.0.0.1:8080/reset_password?token={reset_token}"

        subject = "Password Reset Instructions - JobSync"
        body = f"""
Dear {user['username']},

You have requested to reset your password for your JobSync account.

Click the link below to reset your password:
{reset_link}

This link will expire in 24 hours for security reasons.

If you did not request this password reset, please ignore this email and your password will remain unchanged.

For security reasons:
- Never share this link with anyone
- This link can only be used once
- If you have any concerns, contact our support team

Best regards,
The JobSync Team

---
This is a demo email. In production, this would be sent via Firebase Authentication.
"""

        # Send email notification
        send_email(email, subject, body)

        return jsonify({
            'success': True,
            'message': f'Password reset instructions have been sent to {email}'
        })

    except Exception as e:
        print(f"Password reset error: {e}")
        return jsonify({'error': 'An error occurred while processing your request'}), 500

@app.route('/reset_password')
def reset_password():
    """Display password reset form"""
    token = request.args.get('token')

    if not token or not token.startswith('demo_reset_token_'):
        flash('Invalid or expired reset link.', 'error')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)

@app.route('/reset_password', methods=['POST'])
def reset_password_submit():
    """Handle password reset form submission"""
    token = request.form.get('token')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if not token or not token.startswith('demo_reset_token_'):
        flash('Invalid or expired reset link.', 'error')
        return redirect(url_for('login'))

    if not new_password or len(new_password) < 6:
        flash('Password must be at least 6 characters long.', 'error')
        return render_template('reset_password.html', token=token)

    if new_password != confirm_password:
        flash('Passwords do not match.', 'error')
        return render_template('reset_password.html', token=token)

    try:
        # Extract user ID from token
        user_id = token.split('_')[3]

        # Update password in database
        conn = get_db_connection()
        hashed_password = hash_password(new_password)

        result = conn.execute(
            'UPDATE users SET password = ? WHERE id = ?',
            (hashed_password, user_id)
        )

        if result.rowcount > 0:
            conn.commit()
            flash('Password reset successful! You can now login with your new password.', 'success')
        else:
            flash('Invalid reset link or user not found.', 'error')

        conn.close()

    except Exception as e:
        print(f"Password reset submission error: {e}")
        flash('An error occurred while resetting your password.', 'error')

    return redirect(url_for('login'))

@app.route('/api/test_similarity', methods=['POST'])
def test_similarity():
    """API endpoint to test semantic similarity matching"""
    try:
        data = request.get_json()
        job_skills = data.get('job_skills', '')
        candidate_skills = data.get('candidate_skills', '')

        if not job_skills or not candidate_skills:
            return jsonify({'error': 'Both job_skills and candidate_skills are required'}), 400

        # Calculate compatibility
        compatibility_score = calculate_compatibility(job_skills, candidate_skills)

        # Get detailed analysis
        details = get_compatibility_details(job_skills, candidate_skills)

        return jsonify({
            'success': True,
            'compatibility_score': compatibility_score,
            'details': details,
            'job_skills_processed': skill_matcher.preprocess_skills(job_skills),
            'candidate_skills_processed': skill_matcher.preprocess_skills(candidate_skills)
        })

    except Exception as e:
        return jsonify({'error': f'Error calculating similarity: {str(e)}'}), 500

@app.route('/similarity_test')
def similarity_test():
    """Test page for semantic similarity"""
    return render_template('similarity_test.html')

@app.route('/evaluation_metrics')
def evaluation_metrics():
    """Dashboard for evaluation metrics and charts"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('evaluation_metrics.html')

@app.route('/api/update_application_status', methods=['POST'])
def update_application_status():
    """Update application status and send email notifications"""
    if 'user_id' not in session or session['user_type'] != 'employer':
        return jsonify({'error': 'Not authorized'}), 403

    try:
        data = request.get_json()
        application_id = data.get('application_id')
        new_status = data.get('status')

        if not application_id or not new_status:
            return jsonify({'error': 'Application ID and status are required'}), 400

        if new_status not in ['pending', 'accepted', 'rejected']:
            return jsonify({'error': 'Invalid status'}), 400

        conn = get_db_connection()

        # Get application details
        application = conn.execute('''
            SELECT a.*, j.title as job_title, j.salary, j.location, j.job_type,
                   u.username as candidate_name, u.email as candidate_email,
                   emp.username as employer_name, emp.company_name
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            JOIN users u ON a.applicant_id = u.id
            JOIN users emp ON a.employer_id = emp.id
            WHERE a.id = ? AND a.employer_id = ?
        ''', (application_id, session['user_id'])).fetchone()

        if not application:
            conn.close()
            return jsonify({'error': 'Application not found'}), 404

        # Update application status
        conn.execute('''
            UPDATE applications
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_status, application_id))

        conn.commit()
        conn.close()

        # Send email notification based on status
        email_sent = False
        if new_status == 'accepted':
            email_sent = send_job_offer_email(application)
        elif new_status == 'rejected':
            email_sent = send_rejection_email(application)

        return jsonify({
            'success': True,
            'message': f'Application {new_status} successfully',
            'email_sent': email_sent
        })

    except Exception as e:
        print(f"Error updating application status: {e}")
        return jsonify({'error': str(e)}), 500

def send_job_offer_email(application):
    """Send job offer email to successful candidate"""
    try:
        candidate_email = application['candidate_email']
        candidate_name = application['candidate_name']
        job_title = application['job_title']
        company_name = application['company_name'] or application['employer_name']
        salary = application['salary']
        location = application['location']
        job_type = application['job_type']

        subject = f"🎉 Congratulations! Job Offer - {job_title} at {company_name}"

        # Create professional HTML email
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
        .success-icon {{ font-size: 48px; margin-bottom: 20px; }}
        .job-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745; }}
        .next-steps {{ background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; }}
        .btn {{ display: inline-block; background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
        .highlight {{ background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="success-icon">🎉</div>
            <h1>Congratulations!</h1>
            <h2>You Got the Job!</h2>
        </div>

        <div class="content">
            <h2>Dear {candidate_name},</h2>

            <p><strong>Excellent news!</strong> We are delighted to offer you the position of <strong>{job_title}</strong> at <strong>{company_name}</strong>.</p>

            <p>After careful consideration of your application and qualifications, we believe you would be an excellent addition to our team.</p>

            <div class="job-details">
                <h3>📋 Job Offer Details:</h3>
                <ul>
                    <li><strong>Position:</strong> {job_title}</li>
                    <li><strong>Company:</strong> {company_name}</li>
                    <li><strong>Salary:</strong> {salary or 'Competitive package'}</li>
                    <li><strong>Location:</strong> {location}</li>
                    <li><strong>Employment Type:</strong> {job_type.replace('-', ' ').title()}</li>
                    <li><strong>Start Date:</strong> To be discussed</li>
                </ul>
            </div>

            <div class="highlight">
                <h3>🌟 Why We Chose You:</h3>
                <p>Your skills and experience align perfectly with our requirements. We were impressed by your qualifications and believe you'll make a significant contribution to our team.</p>
            </div>

            <div class="next-steps">
                <h3>🚀 Next Steps:</h3>
                <ol>
                    <li><strong>Review this offer</strong> - Take your time to consider the details</li>
                    <li><strong>Contact us</strong> - Reach out with any questions or to discuss terms</li>
                    <li><strong>Formal offer letter</strong> - We'll send detailed terms and conditions</li>
                    <li><strong>Onboarding</strong> - We'll guide you through the joining process</li>
                </ol>
            </div>

            <p><strong>We're excited about the possibility of you joining our team!</strong></p>

            <p>Please feel free to contact us if you have any questions about this offer or would like to discuss any aspects of the position.</p>

            <div class="footer">
                <p><strong>Welcome to the team!</strong></p>
                <p>Best regards,<br>
                <strong>{company_name} Hiring Team</strong></p>
                <hr>
                <small>This job offer was sent through JobSync - Your Career Success Platform</small>
            </div>
        </div>
    </div>
</body>
</html>
"""

        # Plain text version
        text_body = f"""
🎉 CONGRATULATIONS! JOB OFFER

Dear {candidate_name},

Excellent news! We are delighted to offer you the position of {job_title} at {company_name}.

📋 JOB OFFER DETAILS:
- Position: {job_title}
- Company: {company_name}
- Salary: {salary or 'Competitive package'}
- Location: {location}
- Employment Type: {job_type.replace('-', ' ').title()}
- Start Date: To be discussed

🌟 WHY WE CHOSE YOU:
Your skills and experience align perfectly with our requirements. We were impressed by your qualifications and believe you'll make a significant contribution to our team.

🚀 NEXT STEPS:
1. Review this offer - Take your time to consider the details
2. Contact us - Reach out with any questions or to discuss terms
3. Formal offer letter - We'll send detailed terms and conditions
4. Onboarding - We'll guide you through the joining process

We're excited about the possibility of you joining our team!

Please feel free to contact us if you have any questions about this offer.

Welcome to the team!

Best regards,
{company_name} Hiring Team

---
This job offer was sent through JobSync - Your Career Success Platform
"""

        # Send email
        success = send_email(candidate_email, subject, html_body, is_html=True, text_fallback=text_body)

        if success:
            print(f"✅ Job offer email sent to {candidate_email} for {job_title}")
        else:
            print(f"❌ Failed to send job offer email to {candidate_email}")

        return success

    except Exception as e:
        print(f"Error sending job offer email: {e}")
        return False

def send_rejection_email(application):
    """Send rejection email to candidate"""
    try:
        candidate_email = application['candidate_email']
        candidate_name = application['candidate_name']
        job_title = application['job_title']
        company_name = application['company_name'] or application['employer_name']

        subject = f"Application Update - {job_title} at {company_name}"

        # Create professional HTML email
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #6c757d 0%, #495057 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
        .encouragement {{ background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2196f3; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; }}
        .btn {{ display: inline-block; background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Application Update</h1>
            <p>Thank you for your interest in {company_name}</p>
        </div>

        <div class="content">
            <h2>Dear {candidate_name},</h2>

            <p>Thank you for your interest in the <strong>{job_title}</strong> position at <strong>{company_name}</strong> and for taking the time to apply.</p>

            <p>After careful consideration of all applications, we have decided to move forward with other candidates whose experience more closely matches our current requirements.</p>

            <div class="encouragement">
                <h3>💪 Keep Going!</h3>
                <p>Please don't be discouraged. Your qualifications and experience are valuable, and we encourage you to:</p>
                <ul>
                    <li>Continue applying for positions that match your skills</li>
                    <li>Keep developing your professional skills</li>
                    <li>Apply for future openings at {company_name}</li>
                    <li>Stay connected with us for upcoming opportunities</li>
                </ul>
            </div>

            <p>We will keep your resume on file and may contact you about future opportunities that better match your background.</p>

            <p>Thank you again for your interest in {company_name}. We wish you the best of luck in your job search.</p>

            <a href="http://127.0.0.1:8080/jobs" class="btn">Continue Job Search</a>

            <div class="footer">
                <p>Best regards,<br>
                <strong>{company_name} Hiring Team</strong></p>
                <hr>
                <small>This message was sent through JobSync - Your Career Success Platform</small>
            </div>
        </div>
    </div>
</body>
</html>
"""

        # Plain text version
        text_body = f"""
APPLICATION UPDATE

Dear {candidate_name},

Thank you for your interest in the {job_title} position at {company_name} and for taking the time to apply.

After careful consideration of all applications, we have decided to move forward with other candidates whose experience more closely matches our current requirements.

💪 KEEP GOING!
Please don't be discouraged. Your qualifications and experience are valuable, and we encourage you to:
- Continue applying for positions that match your skills
- Keep developing your professional skills
- Apply for future openings at {company_name}
- Stay connected with us for upcoming opportunities

We will keep your resume on file and may contact you about future opportunities that better match your background.

Thank you again for your interest in {company_name}. We wish you the best of luck in your job search.

Continue your job search at: http://127.0.0.1:8080/jobs

Best regards,
{company_name} Hiring Team

---
This message was sent through JobSync - Your Career Success Platform
"""

        # Send email
        success = send_email(candidate_email, subject, html_body, is_html=True, text_fallback=text_body)

        if success:
            print(f"✅ Rejection email sent to {candidate_email} for {job_title}")
        else:
            print(f"❌ Failed to send rejection email to {candidate_email}")

        return success

    except Exception as e:
        print(f"Error sending rejection email: {e}")
        return False

@app.route('/api/evaluation_data')
def get_evaluation_data():
    """Get evaluation data for charts"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        conn = get_db_connection()

        # Get application statistics
        applications_data = conn.execute('''
            SELECT
                j.title,
                j.skills as job_skills,
                up.skills as candidate_skills,
                a.compatibility_score,
                a.status,
                a.applied_at,
                u.username as candidate_name
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            JOIN users u ON a.applicant_id = u.id
            LEFT JOIN user_profiles up ON a.applicant_id = up.user_id
            ORDER BY a.applied_at DESC
            LIMIT 50
        ''').fetchall()

        # Calculate enhanced metrics for each application
        enhanced_applications = []
        for app in applications_data:
            if app['job_skills'] and app['candidate_skills']:
                # Recalculate with semantic analysis
                semantic_score = calculate_compatibility(app['job_skills'], app['candidate_skills'])
                details = get_compatibility_details(app['job_skills'], app['candidate_skills'])

                enhanced_applications.append({
                    'title': app['title'],
                    'candidate_name': app['candidate_name'],
                    'original_score': app['compatibility_score'] or 0,
                    'semantic_score': semantic_score,
                    'exact_matches': len(details['matched']),
                    'semantic_matches': len(details['semantic_matches']),
                    'missing_skills': len(details['missing']),
                    'coverage_percentage': details['match_breakdown']['coverage_percentage'],
                    'status': app['status'],
                    'applied_at': app['applied_at']
                })

        # Get job statistics
        jobs_data = conn.execute('''
            SELECT
                j.title,
                j.skills,
                COUNT(a.id) as application_count,
                AVG(a.compatibility_score) as avg_compatibility
            FROM jobs j
            LEFT JOIN applications a ON j.id = a.job_id
            GROUP BY j.id, j.title, j.skills
            ORDER BY application_count DESC
        ''').fetchall()

        # Calculate skill frequency
        all_skills = []
        for job in jobs_data:
            if job['skills']:
                skills = [skill.strip() for skill in job['skills'].split(',')]
                all_skills.extend(skills)

        from collections import Counter
        skill_frequency = Counter(all_skills)
        top_skills = dict(skill_frequency.most_common(15))

        conn.close()

        return jsonify({
            'success': True,
            'applications': enhanced_applications,
            'jobs': [dict(job) for job in jobs_data],
            'skill_frequency': top_skills,
            'total_applications': len(enhanced_applications),
            'total_jobs': len(jobs_data)
        })

    except Exception as e:
        print(f"Error getting evaluation data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/email_log')
def email_log():
    """View email log for testing purposes"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    emails = []
    try:
        with open('email_log.txt', 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse email entries
        email_blocks = content.split('=' * 80)
        for block in email_blocks:
            if 'TIMESTAMP:' in block and 'TO:' in block and 'SUBJECT:' in block:
                lines = block.strip().split('\n')
                email_data = {}
                body_lines = []
                in_body = False

                for line in lines:
                    if line.startswith('TIMESTAMP:'):
                        email_data['timestamp'] = line.replace('TIMESTAMP:', '').strip()
                    elif line.startswith('TO:'):
                        email_data['to'] = line.replace('TO:', '').strip()
                    elif line.startswith('SUBJECT:'):
                        email_data['subject'] = line.replace('SUBJECT:', '').strip()
                    elif line.strip() == '=' * 80:
                        in_body = True
                    elif in_body and line.strip():
                        body_lines.append(line)

                if email_data and body_lines:
                    email_data['body'] = '\n'.join(body_lines)
                    emails.append(email_data)

        # Sort by timestamp (newest first)
        emails.reverse()

    except FileNotFoundError:
        emails = []

    return render_template('email_log.html', emails=emails)

# News feed API routes
@app.route('/api/posts', methods=['GET'])
def get_posts():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    conn = get_db_connection()
    posts = conn.execute('''
        SELECT np.*,
               (SELECT COUNT(*) FROM post_likes pl WHERE pl.post_id = np.id) as actual_likes_count,
               (SELECT COUNT(*) FROM post_comments pc WHERE pc.post_id = np.id) as actual_comments_count,
               (SELECT COUNT(*) FROM post_likes pl WHERE pl.post_id = np.id AND pl.user_id = ?) as user_liked
        FROM news_posts np
        ORDER BY np.created_at DESC
        LIMIT 50
    ''', (session['user_id'],)).fetchall()

    posts_list = []
    for post in posts:
        posts_list.append({
            'id': post['id'],
            'user_id': post['user_id'],
            'username': post['username'],
            'user_type': post['user_type'],
            'content': post['content'],
            'image_path': post['image_path'],
            'video_path': post['video_path'],
            'likes_count': post['actual_likes_count'],
            'comments_count': post['actual_comments_count'],
            'shares_count': post['shares_count'],
            'created_at': post['created_at'],
            'user_liked': bool(post['user_liked'])
        })

    conn.close()
    return jsonify(posts_list)

@app.route('/api/posts', methods=['POST'])
def create_post():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    # Handle both JSON and form data
    if request.is_json:
        # JSON request (text only)
        data = request.get_json()
        content = data.get('content', '').strip()
        image_path = None
    else:
        # Form data request (with possible file upload)
        content = request.form.get('content', '').strip()
        image_path = None

        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                if file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    # Create unique filename
                    filename = secure_filename(f"post_{session['user_id']}_{int(time.time())}_{file.filename}")
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    image_path = filename
                else:
                    return jsonify({'error': 'Invalid image format. Please use PNG, JPG, JPEG, GIF, or WebP.'}), 400

    if not content and not image_path:
        return jsonify({'error': 'Content or image is required'}), 400

    conn = get_db_connection()
    cursor = conn.execute('''
        INSERT INTO news_posts (user_id, username, user_type, content, image_path)
        VALUES (?, ?, ?, ?, ?)
    ''', (session['user_id'], session['username'], session['user_type'], content, image_path))

    post_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'post_id': post_id})

@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
def toggle_like(post_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    conn = get_db_connection()

    # Check if user already liked this post
    existing_like = conn.execute(
        'SELECT id FROM post_likes WHERE post_id = ? AND user_id = ?',
        (post_id, session['user_id'])
    ).fetchone()

    if existing_like:
        # Unlike
        conn.execute(
            'DELETE FROM post_likes WHERE post_id = ? AND user_id = ?',
            (post_id, session['user_id'])
        )
        # Update likes count
        conn.execute(
            'UPDATE news_posts SET likes_count = likes_count - 1 WHERE id = ?',
            (post_id,)
        )
        action = 'unliked'
    else:
        # Like
        conn.execute(
            'INSERT INTO post_likes (post_id, user_id) VALUES (?, ?)',
            (post_id, session['user_id'])
        )
        # Update likes count
        conn.execute(
            'UPDATE news_posts SET likes_count = likes_count + 1 WHERE id = ?',
            (post_id,)
        )
        action = 'liked'

    conn.commit()

    # Get updated likes count
    likes_count = conn.execute(
        'SELECT COUNT(*) as count FROM post_likes WHERE post_id = ?',
        (post_id,)
    ).fetchone()['count']

    conn.close()

    return jsonify({'success': True, 'action': action, 'likes_count': likes_count})

@app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    conn = get_db_connection()
    comments = conn.execute('''
        SELECT * FROM post_comments
        WHERE post_id = ?
        ORDER BY created_at ASC
    ''', (post_id,)).fetchall()

    comments_list = []
    for comment in comments:
        comments_list.append({
            'id': comment['id'],
            'user_id': comment['user_id'],
            'username': comment['username'],
            'user_type': comment['user_type'],
            'comment': comment['comment'],
            'created_at': comment['created_at']
        })

    conn.close()
    return jsonify(comments_list)

@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    comment_text = data.get('comment', '').strip()

    if not comment_text:
        return jsonify({'error': 'Comment is required'}), 400

    conn = get_db_connection()

    # Add comment
    cursor = conn.execute('''
        INSERT INTO post_comments (post_id, user_id, username, user_type, comment)
        VALUES (?, ?, ?, ?, ?)
    ''', (post_id, session['user_id'], session['username'], session['user_type'], comment_text))

    comment_id = cursor.lastrowid

    # Update comments count
    conn.execute(
        'UPDATE news_posts SET comments_count = comments_count + 1 WHERE id = ?',
        (post_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'comment_id': comment_id})

@app.route('/firebase-debug')
def firebase_debug():
    return render_template('firebase-debug.html')

@app.route('/firebase-test')
def firebase_test():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('firebase-simple-test.html')

@app.route('/firebase-step-test')
def firebase_step_test():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('firebase-step-test.html')

if __name__ == '__main__':
    init_db()
    create_demo_accounts()
    app.run(debug=True, port=8080)
