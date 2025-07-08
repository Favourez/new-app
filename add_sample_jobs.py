#!/usr/bin/env python3
"""
Simple script to add sample jobs to the database
"""

import sqlite3

def get_db_connection():
    conn = sqlite3.connect('jobportal.db')
    conn.row_factory = sqlite3.Row
    return conn

def add_sample_jobs():
    conn = get_db_connection()
    
    # Sample jobs
    jobs = [
        {
            'employer_id': 2,  # Demo employer
            'title': 'Frontend Developer',
            'description': 'We are looking for a skilled Frontend Developer to join our team. You will be responsible for building user-facing web applications using modern JavaScript frameworks.',
            'requirements': 'Bachelor degree in Computer Science or related field. 2+ years of experience in web development.',
            'skills': 'JavaScript, React, HTML, CSS, Bootstrap',
            'salary': '$60,000 - $80,000',
            'location': 'New York, NY',
            'job_type': 'full-time'
        },
        {
            'employer_id': 2,
            'title': 'Python Developer',
            'description': 'Join our team as a Python Developer. You will work on backend development using Python and Flask.',
            'requirements': '3+ years of Python development experience. Experience with Flask or Django.',
            'skills': 'Python, Flask, SQL, Git',
            'salary': '$70,000 - $90,000',
            'location': 'San Francisco, CA',
            'job_type': 'full-time'
        },
        {
            'employer_id': 2,
            'title': 'Full Stack Developer',
            'description': 'Full Stack Developer needed to work on both frontend and backend development.',
            'requirements': 'Experience with both frontend and backend technologies.',
            'skills': 'JavaScript, Python, React, Flask, SQL',
            'salary': '$75,000 - $95,000',
            'location': 'Austin, TX',
            'job_type': 'full-time'
        }
    ]
    
    for job in jobs:
        try:
            conn.execute('''
                INSERT INTO jobs (employer_id, title, description, requirements, skills, salary, location, job_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job['employer_id'], job['title'], job['description'], 
                job['requirements'], job['skills'], job['salary'], 
                job['location'], job['job_type']
            ))
            print(f"Added job: {job['title']}")
        except Exception as e:
            print(f"Error adding job {job['title']}: {e}")
    
    conn.commit()
    
    # Update demo user skills
    try:
        conn.execute('''
            UPDATE user_profiles 
            SET skills = ?, experience = ?, education = ?
            WHERE user_id = 1
        ''', (
            "Python, JavaScript, React, Flask, SQL, HTML, CSS, Git",
            "2+ years of web development experience. Built several applications using Python Flask and React.",
            "Bachelor's degree in Computer Science."
        ))
        print("Updated demo jobseeker skills")
    except Exception as e:
        print(f"Error updating demo user: {e}")
    
    conn.commit()
    conn.close()
    print("Sample jobs added successfully!")

if __name__ == "__main__":
    add_sample_jobs()
