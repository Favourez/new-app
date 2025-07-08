#!/usr/bin/env python3
"""
Setup test data for CV download functionality
"""

import sqlite3
import os

def setup_test_data():
    """Create sample jobs, applications, and CV for testing"""
    
    # Create uploads directory if it doesn't exist
    uploads_dir = 'static/uploads'
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    
    # Create a sample CV file
    cv_content = """DEMO JOBSEEKER - CURRICULUM VITAE
================================

PERSONAL INFORMATION
Name: Demo Jobseeker
Email: jobseeker@demo.com
Phone: (555) 123-4567

SKILLS
Python, JavaScript, React, Flask, SQL, HTML, CSS, Git

EXPERIENCE
2+ years of web development experience. Built several full-stack applications.

EDUCATION
Bachelor's degree in Computer Science from State University.

PROJECTS
- Personal Portfolio Website (React, CSS)
- Task Management App (Flask, SQLite)
- E-commerce Platform (Python, JavaScript)

Generated for JobSync Demo Application"""
    
    # Save CV file
    cv_filename = 'resume_1_demo_jobseeker_cv.txt'
    cv_path = os.path.join(uploads_dir, cv_filename)
    
    with open(cv_path, 'w', encoding='utf-8') as f:
        f.write(cv_content)
    
    print(f"✅ Created sample CV: {cv_path}")
    
    # Connect to database
    conn = sqlite3.connect('jobportal.db')
    
    # Update demo jobseeker profile
    conn.execute('''
        UPDATE user_profiles 
        SET resume_filename = ?, 
            skills = ?, 
            experience = ?, 
            education = ?
        WHERE user_id = 1
    ''', (
        cv_filename,
        "Python, JavaScript, React, Flask, SQL, HTML, CSS, Git",
        "2+ years of web development experience. Built several full-stack applications using Python Flask and React.",
        "Bachelor's degree in Computer Science from State University."
    ))
    
    # Add sample jobs if they don't exist
    existing_jobs = conn.execute('SELECT COUNT(*) FROM jobs').fetchone()[0]
    
    if existing_jobs == 0:
        sample_jobs = [
            (2, 'Frontend Developer', 'Build amazing user interfaces with React and JavaScript', 'Bachelor degree, 2+ years experience', 'JavaScript, React, HTML, CSS', '$60,000 - $80,000', 'New York, NY', 'full-time'),
            (2, 'Python Developer', 'Backend development with Python and Flask', '3+ years Python experience', 'Python, Flask, SQL, Git', '$70,000 - $90,000', 'San Francisco, CA', 'full-time'),
            (2, 'Full Stack Developer', 'Work on both frontend and backend', 'Full stack experience required', 'JavaScript, Python, React, Flask, SQL', '$75,000 - $95,000', 'Austin, TX', 'full-time')
        ]
        
        for job in sample_jobs:
            conn.execute('''
                INSERT INTO jobs (employer_id, title, description, requirements, skills, salary, location, job_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', job)
        
        print("✅ Added sample jobs")
    
    # Add sample applications if they don't exist
    existing_apps = conn.execute('SELECT COUNT(*) FROM applications').fetchone()[0]
    
    if existing_apps == 0:
        # Get job IDs
        jobs = conn.execute('SELECT id, skills FROM jobs').fetchall()
        
        for job in jobs:
            # Calculate compatibility score
            job_skills = job[1].lower().split(',')
            user_skills = "python, javascript, react, flask, sql, html, css, git".split(',')
            
            matching_skills = 0
            for job_skill in job_skills:
                for user_skill in user_skills:
                    if job_skill.strip() in user_skill.strip() or user_skill.strip() in job_skill.strip():
                        matching_skills += 1
                        break
            
            compatibility = int((matching_skills / len(job_skills)) * 100) if job_skills else 0
            
            # Create application
            conn.execute('''
                INSERT INTO applications (job_id, applicant_id, employer_id, compatibility_score, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (job[0], 1, 2, compatibility, 'pending'))
        
        print("✅ Added sample applications")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 Test setup complete!")
    print("📋 What you can now test:")
    print("1. Login as employer (employer@demo.com / demo123)")
    print("2. Go to Employer Dashboard")
    print("3. See applications with 'Download CV' buttons")
    print("4. Click 'Download CV' to download the sample resume")
    print("5. Click 'View Profile' to see detailed applicant information")
    print("\n🌐 Visit: http://127.0.0.1:8080")

if __name__ == "__main__":
    setup_test_data()
