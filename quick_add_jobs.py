import sqlite3

# Connect to database
conn = sqlite3.connect('jobportal.db')

# Add sample jobs
jobs = [
    (2, 'Frontend Developer', 'Build amazing user interfaces with React and JavaScript', 'Bachelor degree, 2+ years experience', 'JavaScript, React, HTML, CSS', '$60,000 - $80,000', 'New York, NY', 'full-time'),
    (2, 'Python Developer', 'Backend development with Python and Flask', '3+ years Python experience', 'Python, Flask, SQL, Git', '$70,000 - $90,000', 'San Francisco, CA', 'full-time'),
    (2, 'Full Stack Developer', 'Work on both frontend and backend', 'Full stack experience required', 'JavaScript, Python, React, Flask, SQL', '$75,000 - $95,000', 'Austin, TX', 'full-time')
]

for job in jobs:
    conn.execute('''
        INSERT INTO jobs (employer_id, title, description, requirements, skills, salary, location, job_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', job)

# Update demo user skills
conn.execute('''
    UPDATE user_profiles 
    SET skills = ?, experience = ?, education = ?
    WHERE user_id = 1
''', (
    "Python, JavaScript, React, Flask, SQL, HTML, CSS, Git",
    "2+ years of web development experience",
    "Bachelor's degree in Computer Science"
))

conn.commit()
conn.close()
print("Jobs added successfully!")
