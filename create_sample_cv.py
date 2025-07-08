#!/usr/bin/env python3
"""
Create a sample CV file for testing the download functionality
"""

import sqlite3
import os

def create_sample_cv():
    """Create a sample CV file and update the database"""
    
    # Create uploads directory if it doesn't exist
    uploads_dir = 'static/uploads'
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    
    # Create a simple text file as a sample CV (in real app, this would be a PDF)
    cv_content = """
DEMO JOBSEEKER - CURRICULUM VITAE
================================

PERSONAL INFORMATION
-------------------
Name: Demo Jobseeker
Email: jobseeker@demo.com
Phone: (555) 123-4567
Location: New York, NY

PROFESSIONAL SUMMARY
-------------------
Experienced web developer with 2+ years of experience in full-stack development.
Proficient in Python, JavaScript, React, and Flask. Passionate about creating
efficient and user-friendly web applications.

TECHNICAL SKILLS
---------------
• Programming Languages: Python, JavaScript, HTML, CSS
• Frameworks: React, Flask, Bootstrap
• Databases: SQL, SQLite, PostgreSQL
• Tools: Git, GitHub, VS Code
• Other: RESTful APIs, Responsive Design

WORK EXPERIENCE
--------------
Junior Web Developer | Tech Solutions Inc. | 2022 - Present
• Developed and maintained web applications using Python Flask and React
• Collaborated with cross-functional teams to deliver high-quality software
• Implemented responsive designs and improved user experience
• Participated in code reviews and agile development processes

Intern Web Developer | StartUp Co. | 2021 - 2022
• Assisted in building company website using HTML, CSS, and JavaScript
• Learned modern web development practices and frameworks
• Contributed to bug fixes and feature enhancements

EDUCATION
---------
Bachelor of Science in Computer Science
State University | 2018 - 2022
GPA: 3.7/4.0

Relevant Coursework:
• Data Structures and Algorithms
• Web Development
• Database Systems
• Software Engineering

PROJECTS
--------
Personal Portfolio Website
• Built responsive portfolio website using React and CSS
• Implemented contact form with email integration
• Deployed on GitHub Pages

Task Management App
• Developed full-stack task management application
• Used Flask backend with SQLite database
• Implemented user authentication and CRUD operations

CERTIFICATIONS
-------------
• Python Programming Certificate - Online Academy (2022)
• React Development Course - Web Dev Institute (2021)

LANGUAGES
---------
• English (Native)
• Spanish (Conversational)

REFERENCES
----------
Available upon request

---
Generated for JobSync Demo Application
"""
    
    # Save the CV content to a file
    cv_filename = 'resume_1_demo_jobseeker_cv.txt'
    cv_path = os.path.join(uploads_dir, cv_filename)
    
    with open(cv_path, 'w', encoding='utf-8') as f:
        f.write(cv_content)
    
    print(f"✅ Created sample CV: {cv_path}")
    
    # Update the database to reference this CV
    conn = sqlite3.connect('jobportal.db')
    
    # Update demo jobseeker's profile with the CV filename
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
        "2+ years of web development experience. Built several full-stack applications using Python Flask and React. Experience with database design and API development.",
        "Bachelor's degree in Computer Science from State University (2018-2022). GPA: 3.7/4.0. Relevant coursework in web development, data structures, and software engineering."
    ))
    
    conn.commit()
    conn.close()
    
    print("✅ Updated demo jobseeker profile with CV information")
    print(f"📄 CV file location: {cv_path}")
    print("🎯 Employers can now download this CV from the dashboard!")

if __name__ == "__main__":
    create_sample_cv()
