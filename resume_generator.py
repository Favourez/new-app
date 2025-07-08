#!/usr/bin/env python3
"""
AI Resume Generator & Parser Training System
==========================================

This script generates 1200 diverse synthetic resumes and trains a custom
AI model for resume parsing and skill extraction.
"""

import random
import json
import os
from datetime import datetime, timedelta
from faker import Faker
import pandas as pd

class ResumeGenerator:
    """Generate realistic synthetic resumes for training"""
    
    def __init__(self):
        self.fake = Faker(['en_US', 'en_GB', 'en_CA'])
        
        # Comprehensive skill sets by category
        self.technical_skills = {
            'programming': [
                'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 'Swift',
                'Kotlin', 'PHP', 'Ruby', 'Scala', 'R', 'MATLAB', 'Perl', 'TypeScript',
                'Dart', 'Objective-C', 'Assembly', 'COBOL', 'Fortran', 'Haskell'
            ],
            'web_frontend': [
                'React', 'Angular', 'Vue.js', 'HTML5', 'CSS3', 'SASS', 'LESS',
                'Bootstrap', 'Tailwind CSS', 'jQuery', 'Webpack', 'Babel',
                'Next.js', 'Nuxt.js', 'Svelte', 'Ember.js'
            ],
            'web_backend': [
                'Node.js', 'Express.js', 'Django', 'Flask', 'FastAPI', 'Spring Boot',
                'Laravel', 'Ruby on Rails', 'ASP.NET', 'Gin', 'Echo', 'Fiber'
            ],
            'databases': [
                'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
                'Oracle', 'SQL Server', 'SQLite', 'Cassandra', 'DynamoDB',
                'Neo4j', 'InfluxDB', 'CouchDB', 'MariaDB'
            ],
            'cloud_devops': [
                'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins',
                'Terraform', 'Ansible', 'Git', 'GitLab', 'GitHub Actions',
                'CircleCI', 'Travis CI', 'Helm', 'Istio', 'Prometheus', 'Grafana'
            ],
            'data_science': [
                'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch',
                'Scikit-learn', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn',
                'Jupyter', 'Apache Spark', 'Hadoop', 'Tableau', 'Power BI',
                'Keras', 'OpenCV', 'NLTK', 'spaCy', 'Plotly'
            ],
            'mobile': [
                'iOS Development', 'Android Development', 'React Native', 'Flutter',
                'Xamarin', 'Ionic', 'Cordova', 'Unity', 'Unreal Engine'
            ],
            'other_tech': [
                'Microservices', 'REST API', 'GraphQL', 'gRPC', 'Blockchain',
                'IoT', 'AR/VR', 'Computer Vision', 'NLP', 'Cybersecurity',
                'Penetration Testing', 'Network Security', 'CISSP', 'CEH'
            ]
        }
        
        self.soft_skills = [
            'Leadership', 'Communication', 'Problem Solving', 'Teamwork',
            'Project Management', 'Agile', 'Scrum', 'Critical Thinking',
            'Creativity', 'Adaptability', 'Time Management', 'Public Speaking',
            'Negotiation', 'Mentoring', 'Strategic Planning', 'Decision Making'
        ]
        
        self.job_titles = [
            'Software Engineer', 'Senior Software Engineer', 'Lead Software Engineer',
            'Full Stack Developer', 'Frontend Developer', 'Backend Developer',
            'Data Scientist', 'Data Analyst', 'Machine Learning Engineer',
            'DevOps Engineer', 'Cloud Architect', 'System Administrator',
            'Product Manager', 'Technical Lead', 'Engineering Manager',
            'Mobile Developer', 'Web Developer', 'Database Administrator',
            'Security Engineer', 'QA Engineer', 'Site Reliability Engineer',
            'AI Engineer', 'Research Scientist', 'Solutions Architect'
        ]
        
        self.companies = [
            'Google', 'Microsoft', 'Amazon', 'Apple', 'Meta', 'Netflix',
            'Tesla', 'Uber', 'Airbnb', 'Spotify', 'Slack', 'Zoom',
            'Salesforce', 'Oracle', 'IBM', 'Intel', 'NVIDIA', 'Adobe',
            'Atlassian', 'Shopify', 'Square', 'Stripe', 'Twilio', 'GitHub',
            'TechCorp Solutions', 'InnovateTech', 'DataDriven Inc', 'CloudFirst',
            'NextGen Systems', 'Digital Dynamics', 'Smart Solutions Ltd',
            'Future Technologies', 'Quantum Computing Co', 'AI Innovations'
        ]
        
        self.universities = [
            'MIT', 'Stanford University', 'Carnegie Mellon University',
            'UC Berkeley', 'Harvard University', 'Caltech', 'Princeton',
            'University of Washington', 'Georgia Tech', 'Cornell University',
            'University of Texas at Austin', 'University of Illinois',
            'Purdue University', 'University of Michigan', 'UCLA',
            'Columbia University', 'Yale University', 'NYU', 'USC',
            'Boston University', 'Northeastern University', 'RIT'
        ]
        
        self.degrees = [
            'Computer Science', 'Software Engineering', 'Data Science',
            'Information Technology', 'Electrical Engineering',
            'Computer Engineering', 'Mathematics', 'Statistics',
            'Information Systems', 'Cybersecurity', 'AI and Machine Learning'
        ]
        
        self.certifications = [
            'AWS Certified Solutions Architect', 'Google Cloud Professional',
            'Microsoft Azure Fundamentals', 'Certified Kubernetes Administrator',
            'PMP', 'Scrum Master', 'CISSP', 'CEH', 'CISA', 'CompTIA Security+',
            'Oracle Certified Professional', 'Salesforce Certified',
            'TensorFlow Developer Certificate', 'Deep Learning Specialization'
        ]
    
    def generate_skills(self, job_category='general', num_skills=None):
        """Generate relevant skills based on job category"""
        if num_skills is None:
            num_skills = random.randint(5, 12)
        
        skills = []
        
        # Add technical skills based on category
        if job_category in ['software', 'fullstack', 'backend']:
            skills.extend(random.sample(self.technical_skills['programming'], random.randint(2, 4)))
            skills.extend(random.sample(self.technical_skills['web_backend'], random.randint(1, 3)))
            skills.extend(random.sample(self.technical_skills['databases'], random.randint(1, 2)))
        
        elif job_category in ['frontend', 'web']:
            skills.extend(random.sample(self.technical_skills['web_frontend'], random.randint(3, 5)))
            skills.extend(random.sample(self.technical_skills['programming'], random.randint(1, 2)))
        
        elif job_category == 'data':
            skills.extend(random.sample(self.technical_skills['data_science'], random.randint(4, 6)))
            skills.extend(random.sample(self.technical_skills['programming'], random.randint(1, 2)))
        
        elif job_category == 'devops':
            skills.extend(random.sample(self.technical_skills['cloud_devops'], random.randint(4, 6)))
            skills.extend(random.sample(self.technical_skills['programming'], random.randint(1, 2)))
        
        elif job_category == 'mobile':
            skills.extend(random.sample(self.technical_skills['mobile'], random.randint(2, 4)))
            skills.extend(random.sample(self.technical_skills['programming'], random.randint(1, 2)))
        
        else:  # general
            # Mix from all categories
            for category in self.technical_skills.values():
                if random.random() > 0.5:
                    skills.extend(random.sample(category, random.randint(1, 2)))
        
        # Add soft skills
        skills.extend(random.sample(self.soft_skills, random.randint(2, 4)))
        
        # Ensure we don't exceed the desired number
        if len(skills) > num_skills:
            skills = random.sample(skills, num_skills)
        
        return list(set(skills))  # Remove duplicates
    
    def generate_work_experience(self, years_experience):
        """Generate realistic work experience"""
        experiences = []
        current_date = datetime.now()
        
        # Determine number of jobs based on experience
        if years_experience <= 2:
            num_jobs = random.randint(1, 2)
        elif years_experience <= 5:
            num_jobs = random.randint(2, 3)
        elif years_experience <= 10:
            num_jobs = random.randint(3, 4)
        else:
            num_jobs = random.randint(4, 6)
        
        for i in range(num_jobs):
            # Calculate job duration
            if i == 0:  # Current job
                start_date = current_date - timedelta(days=random.randint(180, 1095))  # 6 months to 3 years
                end_date = "Present"
            else:
                years_back = sum(random.randint(1, 3) for _ in range(i))
                start_date = current_date - timedelta(days=years_back * 365 + random.randint(0, 365))
                end_date = start_date + timedelta(days=random.randint(365, 1095))
            
            experience = {
                'title': random.choice(self.job_titles),
                'company': random.choice(self.companies),
                'start_date': start_date.strftime('%B %Y') if isinstance(start_date, datetime) else start_date,
                'end_date': end_date.strftime('%B %Y') if isinstance(end_date, datetime) else end_date,
                'description': self.generate_job_description()
            }
            
            experiences.append(experience)
        
        return experiences
    
    def generate_job_description(self):
        """Generate realistic job descriptions"""
        descriptions = [
            "Developed and maintained web applications using modern frameworks and technologies.",
            "Collaborated with cross-functional teams to deliver high-quality software solutions.",
            "Implemented automated testing and CI/CD pipelines to improve development efficiency.",
            "Designed and optimized database schemas for improved performance and scalability.",
            "Led technical discussions and mentored junior developers on best practices.",
            "Built RESTful APIs and microservices architecture for scalable applications.",
            "Worked with cloud platforms to deploy and manage production applications.",
            "Analyzed complex data sets to derive actionable business insights.",
            "Implemented machine learning models for predictive analytics and automation.",
            "Managed project timelines and coordinated with stakeholders for successful delivery."
        ]
        
        return random.choice(descriptions)
    
    def generate_education(self):
        """Generate education background"""
        degree_level = random.choice(['Bachelor', 'Master', 'PhD'])
        degree = random.choice(self.degrees)
        university = random.choice(self.universities)
        
        # Generate graduation year
        current_year = datetime.now().year
        grad_year = random.randint(current_year - 15, current_year - 1)
        
        return {
            'degree': f"{degree_level} of Science in {degree}",
            'university': university,
            'graduation_year': grad_year,
            'gpa': round(random.uniform(3.0, 4.0), 2) if random.random() > 0.3 else None
        }
    
    def generate_resume(self, resume_id):
        """Generate a complete resume"""
        
        # Basic info
        name = self.fake.name()
        email = self.fake.email()
        phone = self.fake.phone_number()
        location = f"{self.fake.city()}, {self.fake.state_abbr()}"
        
        # Experience level
        years_experience = random.randint(0, 15)
        
        # Job category for skill relevance
        job_categories = ['software', 'frontend', 'backend', 'fullstack', 'data', 'devops', 'mobile', 'general']
        job_category = random.choice(job_categories)
        
        # Generate components
        skills = self.generate_skills(job_category)
        work_experience = self.generate_work_experience(years_experience)
        education = self.generate_education()
        
        # Certifications (optional)
        certifications = []
        if random.random() > 0.6:  # 40% chance of having certifications
            num_certs = random.randint(1, 3)
            certifications = random.sample(self.certifications, num_certs)
        
        # Current job title
        current_title = work_experience[0]['title'] if work_experience else random.choice(self.job_titles)
        
        resume = {
            'id': resume_id,
            'name': name,
            'email': email,
            'phone': phone,
            'location': location,
            'title': current_title,
            'years_experience': years_experience,
            'skills': skills,
            'work_experience': work_experience,
            'education': education,
            'certifications': certifications,
            'job_category': job_category
        }
        
        return resume
    
    def format_resume_text(self, resume):
        """Convert resume dict to formatted text"""
        
        text = f"""
{resume['name']}
{resume['title']}

Contact Information:
Email: {resume['email']}
Phone: {resume['phone']}
Location: {resume['location']}

Professional Summary:
{resume['title']} with {resume['years_experience']} years of experience in software development and technology.

Skills:
{', '.join(resume['skills'])}

Work Experience:
"""
        
        for exp in resume['work_experience']:
            text += f"""
{exp['title']} at {exp['company']}
{exp['start_date']} - {exp['end_date']}
• {exp['description']}
"""
        
        text += f"""
Education:
{resume['education']['degree']}
{resume['education']['university']}, {resume['education']['graduation_year']}
"""
        
        if resume['education']['gpa']:
            text += f"GPA: {resume['education']['gpa']}\n"
        
        if resume['certifications']:
            text += f"""
Certifications:
{', '.join(resume['certifications'])}
"""
        
        return text.strip()
    
    def generate_dataset(self, num_resumes=1200):
        """Generate complete dataset of resumes"""
        
        print(f"🚀 Generating {num_resumes} synthetic resumes...")
        
        resumes = []
        resume_texts = []
        
        for i in range(num_resumes):
            if (i + 1) % 100 == 0:
                print(f"Generated {i + 1}/{num_resumes} resumes...")
            
            resume = self.generate_resume(i + 1)
            resume_text = self.format_resume_text(resume)
            
            resumes.append(resume)
            resume_texts.append(resume_text)
        
        print(f"✅ Generated {num_resumes} resumes successfully!")
        
        return resumes, resume_texts

def save_dataset(resumes, resume_texts, output_dir='resume_dataset'):
    """Save generated dataset to files"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save structured data as JSON
    with open(f'{output_dir}/resumes_structured.json', 'w') as f:
        json.dump(resumes, f, indent=2, default=str)
    
    # Save text data
    with open(f'{output_dir}/resumes_text.txt', 'w') as f:
        for i, text in enumerate(resume_texts):
            f.write(f"=== RESUME {i+1} ===\n")
            f.write(text)
            f.write("\n\n")
    
    # Save as CSV for easy analysis
    df_data = []
    for resume in resumes:
        df_data.append({
            'id': resume['id'],
            'name': resume['name'],
            'email': resume['email'],
            'phone': resume['phone'],
            'title': resume['title'],
            'years_experience': resume['years_experience'],
            'skills': ', '.join(resume['skills']),
            'education_degree': resume['education']['degree'],
            'education_university': resume['education']['university'],
            'job_category': resume['job_category'],
            'num_skills': len(resume['skills']),
            'num_jobs': len(resume['work_experience']),
            'has_certifications': len(resume['certifications']) > 0
        })
    
    df = pd.DataFrame(df_data)
    df.to_csv(f'{output_dir}/resumes_summary.csv', index=False)
    
    print(f"📁 Dataset saved to '{output_dir}/' directory")
    print(f"   - resumes_structured.json: Complete structured data")
    print(f"   - resumes_text.txt: Formatted resume texts")
    print(f"   - resumes_summary.csv: Summary statistics")

def main():
    """Main function to generate resume dataset"""
    
    print("🎯 AI Resume Generator & Training System")
    print("=" * 50)
    
    # Initialize generator
    generator = ResumeGenerator()
    
    # Generate dataset
    resumes, resume_texts = generator.generate_dataset(1200)
    
    # Save dataset
    save_dataset(resumes, resume_texts)
    
    # Print statistics
    print("\n📊 Dataset Statistics:")
    print(f"Total Resumes: {len(resumes)}")
    print(f"Average Skills per Resume: {sum(len(r['skills']) for r in resumes) / len(resumes):.1f}")
    print(f"Average Experience: {sum(r['years_experience'] for r in resumes) / len(resumes):.1f} years")
    
    # Skill distribution
    all_skills = []
    for resume in resumes:
        all_skills.extend(resume['skills'])
    
    from collections import Counter
    skill_counts = Counter(all_skills)
    print(f"Total Unique Skills: {len(skill_counts)}")
    print(f"Top 5 Skills: {list(skill_counts.most_common(5))}")
    
    print("\n🎉 Resume generation completed!")
    print("Next step: Run 'python train_resume_parser.py' to train the AI model")

if __name__ == "__main__":
    main()
