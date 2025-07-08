#!/usr/bin/env python3
"""
Add Sample Data for Evaluation Metrics
======================================

This script adds sample jobs and applications to demonstrate the evaluation metrics dashboard.
"""

import sqlite3
import hashlib
from datetime import datetime, timedelta
import random

def get_db_connection():
    conn = sqlite3.connect('jobportal.db', timeout=30)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_sample_jobs():
    """Add sample jobs with various skill requirements"""
    
    sample_jobs = [
        {
            'title': 'Senior Python Developer',
            'description': 'We are looking for an experienced Python developer to join our backend team.',
            'requirements': 'Bachelor degree in Computer Science, 3+ years Python experience',
            'skills': 'Python, Django, PostgreSQL, Redis, Docker, AWS',
            'salary': 'CFA 900,000 - CFA 1,200,000',
            'location': 'Yaoundé, Cameroon',
            'job_type': 'full-time'
        },
        {
            'title': 'Frontend React Developer',
            'description': 'Join our frontend team to build amazing user interfaces.',
            'requirements': '2+ years React experience, strong JavaScript skills',
            'skills': 'React, JavaScript, TypeScript, CSS, HTML, Redux',
            'salary': 'CFA 700,000 - CFA 950,000',
            'location': 'Douala, Cameroon',
            'job_type': 'full-time'
        },
        {
            'title': 'Data Scientist',
            'description': 'Analyze data and build machine learning models.',
            'requirements': 'Masters in Data Science or related field',
            'skills': 'Python, Machine Learning, TensorFlow, Pandas, SQL, Statistics',
            'salary': 'CFA 1,000,000 - CFA 1,400,000',
            'location': 'Yaoundé, Cameroon',
            'job_type': 'full-time'
        },
        {
            'title': 'DevOps Engineer',
            'description': 'Manage infrastructure and deployment pipelines.',
            'requirements': '3+ years DevOps experience',
            'skills': 'Docker, Kubernetes, AWS, Jenkins, Linux, Python',
            'salary': 'CFA 850,000 - CFA 1,100,000',
            'location': 'Douala, Cameroon',
            'job_type': 'full-time'
        },
        {
            'title': 'Mobile App Developer',
            'description': 'Develop mobile applications for iOS and Android.',
            'requirements': '2+ years mobile development experience',
            'skills': 'React Native, JavaScript, iOS, Android, Firebase',
            'salary': 'CFA 750,000 - CFA 1,000,000',
            'location': 'Yaoundé, Cameroon',
            'job_type': 'full-time'
        }
    ]
    
    conn = get_db_connection()
    
    for job in sample_jobs:
        conn.execute('''
            INSERT OR IGNORE INTO jobs (employer_id, title, description, requirements, skills, salary, location, job_type, posted_at)
            VALUES (2, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job['title'],
            job['description'],
            job['requirements'],
            job['skills'],
            job['salary'],
            job['location'],
            job['job_type'],
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
    
    conn.commit()
    conn.close()
    print(f"✅ Added {len(sample_jobs)} sample jobs")

def add_sample_candidates():
    """Add sample candidates with various skill sets"""
    
    sample_candidates = [
        {
            'username': 'Alice Johnson',
            'email': 'alice@example.com',
            'skills': 'Python, Django, PostgreSQL, JavaScript, React'
        },
        {
            'username': 'Bob Smith',
            'email': 'bob@example.com',
            'skills': 'JavaScript, React, TypeScript, Node.js, MongoDB'
        },
        {
            'username': 'Carol Davis',
            'email': 'carol@example.com',
            'skills': 'Python, Machine Learning, TensorFlow, Pandas, SQL'
        },
        {
            'username': 'David Wilson',
            'email': 'david@example.com',
            'skills': 'Docker, Kubernetes, AWS, Linux, Python, Jenkins'
        },
        {
            'username': 'Eva Brown',
            'email': 'eva@example.com',
            'skills': 'React Native, JavaScript, iOS, Android, Firebase'
        }
    ]
    
    conn = get_db_connection()
    password_hash = hash_password('demo123')
    
    for candidate in sample_candidates:
        # Insert user
        cursor = conn.execute('''
            INSERT OR IGNORE INTO users (username, email, password, user_type, created_at)
            VALUES (?, ?, ?, 'jobseeker', ?)
        ''', (
            candidate['username'],
            candidate['email'],
            password_hash,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        if cursor.rowcount > 0:
            user_id = cursor.lastrowid
            
            # Insert profile
            conn.execute('''
                INSERT OR IGNORE INTO user_profiles (user_id, skills, experience, education)
                VALUES (?, ?, ?, ?)
            ''', (
                user_id,
                candidate['skills'],
                '2-3 years experience',
                'Bachelor degree in Computer Science'
            ))
    
    conn.commit()
    conn.close()
    print(f"✅ Added {len(sample_candidates)} sample candidates")

def add_sample_applications():
    """Add sample applications with calculated compatibility scores"""
    
    conn = get_db_connection()
    
    # Get jobs and candidates
    jobs = conn.execute('SELECT id, skills FROM jobs WHERE employer_id = 2').fetchall()
    candidates = conn.execute('''
        SELECT u.id, up.skills 
        FROM users u 
        JOIN user_profiles up ON u.id = up.user_id 
        WHERE u.user_type = "jobseeker" AND u.email LIKE "%@example.com"
    ''').fetchall()
    
    # Import the compatibility function
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from app import calculate_compatibility
    
    applications_added = 0
    
    for job in jobs:
        # Randomly select 2-4 candidates to apply for each job
        num_applicants = random.randint(2, min(4, len(candidates)))
        selected_candidates = random.sample(list(candidates), num_applicants)
        
        for candidate in selected_candidates:
            if job['skills'] and candidate['skills']:
                # Calculate compatibility score
                compatibility_score = calculate_compatibility(job['skills'], candidate['skills'])
                
                # Random application date within last 30 days
                days_ago = random.randint(1, 30)
                applied_at = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
                
                # Random status based on compatibility score
                if compatibility_score >= 80:
                    status = random.choice(['pending', 'accepted', 'accepted'])
                elif compatibility_score >= 60:
                    status = random.choice(['pending', 'pending', 'accepted'])
                else:
                    status = random.choice(['pending', 'rejected'])
                
                conn.execute('''
                    INSERT OR IGNORE INTO applications 
                    (job_id, applicant_id, employer_id, compatibility_score, status, applied_at)
                    VALUES (?, ?, 2, ?, ?, ?)
                ''', (
                    job['id'],
                    candidate['id'],
                    compatibility_score,
                    status,
                    applied_at
                ))
                
                applications_added += 1
    
    conn.commit()
    conn.close()
    print(f"✅ Added {applications_added} sample applications")

def main():
    """Main function to add all sample data"""
    print("🚀 Adding Sample Data for Evaluation Metrics")
    print("=" * 50)
    
    try:
        add_sample_jobs()
        add_sample_candidates()
        add_sample_applications()
        
        print("\n🎉 Sample data added successfully!")
        print("✅ You can now view comprehensive evaluation metrics")
        print("📊 Visit: http://127.0.0.1:8080/evaluation_metrics")
        
    except Exception as e:
        print(f"\n❌ Error adding sample data: {e}")

if __name__ == "__main__":
    main()
