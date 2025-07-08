#!/usr/bin/env python3
"""
Test script to create sample job postings and test the compatibility system
"""

import sqlite3
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('jobportal.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_sample_jobs():
    """Create sample job postings for testing"""
    conn = get_db_connection()
    
    # Sample jobs with different skill requirements
    sample_jobs = [
        {
            'employer_id': 2,  # Demo employer ID
            'title': 'Frontend Developer',
            'description': 'We are looking for a skilled Frontend Developer to join our team. You will be responsible for building user-facing web applications using modern JavaScript frameworks.',
            'requirements': 'Bachelor\'s degree in Computer Science or related field. 2+ years of experience in web development. Strong problem-solving skills.',
            'skills': 'JavaScript, React, HTML, CSS, Bootstrap',
            'salary': '$60,000 - $80,000',
            'location': 'New York, NY',
            'job_type': 'full-time'
        },
        {
            'employer_id': 2,
            'title': 'Full Stack Python Developer',
            'description': 'Join our dynamic team as a Full Stack Python Developer. You will work on both frontend and backend development using Python and modern web technologies.',
            'requirements': '3+ years of Python development experience. Experience with web frameworks like Flask or Django. Knowledge of databases and API development.',
            'skills': 'Python, Flask, JavaScript, SQL, Git',
            'salary': '$70,000 - $90,000',
            'location': 'San Francisco, CA',
            'job_type': 'full-time'
        },
        {
            'employer_id': 2,
            'title': 'Data Scientist',
            'description': 'We are seeking a Data Scientist to analyze complex datasets and provide insights to drive business decisions. You will work with machine learning algorithms and statistical models.',
            'requirements': 'Master\'s degree in Data Science, Statistics, or related field. Experience with machine learning and data visualization. Strong analytical skills.',
            'skills': 'Python, Machine Learning, SQL, Pandas, NumPy',
            'salary': '$80,000 - $100,000',
            'location': 'Boston, MA',
            'job_type': 'full-time'
        },
        {
            'employer_id': 2,
            'title': 'UI/UX Designer',
            'description': 'Creative UI/UX Designer needed to design intuitive and engaging user interfaces. You will collaborate with developers and product managers to create amazing user experiences.',
            'requirements': 'Portfolio demonstrating UI/UX design skills. Experience with design tools like Figma or Adobe Creative Suite. Understanding of user-centered design principles.',
            'skills': 'Figma, Adobe Photoshop, UI Design, UX Design, Prototyping',
            'salary': '$55,000 - $75,000',
            'location': 'Austin, TX',
            'job_type': 'full-time'
        },
        {
            'employer_id': 2,
            'title': 'DevOps Engineer',
            'description': 'DevOps Engineer to manage our cloud infrastructure and deployment pipelines. You will work with containerization, CI/CD, and cloud platforms.',
            'requirements': 'Experience with cloud platforms (AWS, Azure, or GCP). Knowledge of containerization and orchestration. Scripting and automation skills.',
            'skills': 'Docker, Kubernetes, AWS, Jenkins, Python',
            'salary': '$75,000 - $95,000',
            'location': 'Seattle, WA',
            'job_type': 'full-time'
        }
    ]
    
    # Insert sample jobs
    for job in sample_jobs:
        try:
            cursor = conn.execute('''
                INSERT INTO jobs (employer_id, title, description, requirements, skills, salary, location, job_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job['employer_id'], job['title'], job['description'], 
                job['requirements'], job['skills'], job['salary'], 
                job['location'], job['job_type']
            ))
            print(f"✅ Created job: {job['title']}")
        except Exception as e:
            print(f"❌ Error creating job {job['title']}: {e}")
    
    conn.commit()
    conn.close()
    print(f"\n🎉 Sample jobs created successfully!")

def update_demo_user_skills():
    """Update demo jobseeker with relevant skills for testing compatibility"""
    conn = get_db_connection()
    
    # Update demo jobseeker skills
    demo_skills = "Python, JavaScript, React, Flask, SQL, HTML, CSS, Git"
    
    try:
        conn.execute('''
            UPDATE user_profiles 
            SET skills = ?, experience = ?, education = ?
            WHERE user_id = 1
        ''', (
            demo_skills,
            "2+ years of web development experience. Built several full-stack applications using Python Flask and React. Experience with database design and API development.",
            "Bachelor's degree in Computer Science. Completed online courses in web development and data science."
        ))
        conn.commit()
        print(f"✅ Updated demo jobseeker skills: {demo_skills}")
    except Exception as e:
        print(f"❌ Error updating demo user skills: {e}")
    
    conn.close()

def test_compatibility():
    """Test the compatibility calculation"""
    from app import calculate_compatibility
    
    print("\n🧪 Testing Compatibility Calculation:")
    print("-" * 50)
    
    # Test cases
    test_cases = [
        {
            'job_skills': 'Python, Flask, JavaScript, SQL, Git',
            'user_skills': 'Python, JavaScript, React, Flask, SQL, HTML, CSS, Git',
            'expected': 'High (100%)'
        },
        {
            'job_skills': 'JavaScript, React, HTML, CSS, Bootstrap',
            'user_skills': 'Python, JavaScript, React, Flask, SQL, HTML, CSS, Git',
            'expected': 'High (80%)'
        },
        {
            'job_skills': 'Python, Machine Learning, SQL, Pandas, NumPy',
            'user_skills': 'Python, JavaScript, React, Flask, SQL, HTML, CSS, Git',
            'expected': 'Medium (40%)'
        },
        {
            'job_skills': 'Figma, Adobe Photoshop, UI Design, UX Design, Prototyping',
            'user_skills': 'Python, JavaScript, React, Flask, SQL, HTML, CSS, Git',
            'expected': 'Low (0%)'
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        compatibility = calculate_compatibility(test['job_skills'], test['user_skills'])
        print(f"Test {i}: {compatibility}% - {test['expected']}")
        print(f"  Job Skills: {test['job_skills']}")
        print(f"  User Skills: {test['user_skills']}")
        print()

def show_jobs_with_compatibility():
    """Show all jobs with compatibility scores"""
    conn = get_db_connection()
    
    # Get demo user skills
    user_profile = conn.execute(
        'SELECT skills FROM user_profiles WHERE user_id = 1'
    ).fetchone()
    
    if not user_profile or not user_profile['skills']:
        print("❌ Demo user has no skills set")
        return
    
    user_skills = user_profile['skills']
    print(f"\n👤 Demo User Skills: {user_skills}")
    print("\n📋 Available Jobs with Compatibility Scores:")
    print("=" * 80)
    
    # Get all jobs
    jobs = conn.execute(
        'SELECT * FROM jobs ORDER BY posted_at DESC'
    ).fetchall()
    
    if not jobs:
        print("No jobs found in database")
        return
    
    from app import calculate_compatibility
    
    for job in jobs:
        compatibility = calculate_compatibility(job['skills'], user_skills)
        
        # Color coding based on compatibility
        if compatibility >= 70:
            status = "🟢 EXCELLENT MATCH"
        elif compatibility >= 50:
            status = "🟡 GOOD MATCH"
        elif compatibility >= 30:
            status = "🟠 PARTIAL MATCH"
        else:
            status = "🔴 LOW MATCH"
        
        print(f"\n📄 {job['title']}")
        print(f"   Company: Demo Tech Company")
        print(f"   Location: {job['location']}")
        print(f"   Salary: {job['salary']}")
        print(f"   Required Skills: {job['skills']}")
        print(f"   Compatibility: {compatibility}% {status}")
        print(f"   Description: {job['description'][:100]}...")
    
    conn.close()

if __name__ == "__main__":
    print("🚀 JobSync Job Posting Test Script")
    print("=" * 50)
    
    # Create sample jobs
    create_sample_jobs()
    
    # Update demo user skills
    update_demo_user_skills()
    
    # Test compatibility calculation
    test_compatibility()
    
    # Show jobs with compatibility
    show_jobs_with_compatibility()
    
    print("\n✅ Test completed! You can now:")
    print("1. Login as jobseeker@demo.com / demo123")
    print("2. Go to 'Browse Jobs' to see compatibility scores")
    print("3. Login as employer@demo.com / demo123")
    print("4. Go to 'Post Job' to create new job postings")
    print("\n🌐 Visit: http://127.0.0.1:8080")
