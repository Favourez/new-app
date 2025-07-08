#!/usr/bin/env python3
"""
Excel Report Generator for JobSync AI Resume Parser
=================================================

Generates a comprehensive Excel report with 40 users showing:
- User ID and Name
- Extracted Skills from AI parsing
- Job Required Skills
- Percentage Matching
- Additional analytics
"""

import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class JobSyncReportGenerator:
    """Generate comprehensive Excel reports for JobSync"""
    
    def __init__(self):
        self.fake = Faker()
        
        # Comprehensive skill sets
        self.all_skills = [
            # Programming Languages
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 'Swift',
            'Kotlin', 'PHP', 'Ruby', 'Scala', 'R', 'MATLAB', 'TypeScript', 'Dart',
            
            # Web Technologies
            'React', 'Angular', 'Vue.js', 'HTML5', 'CSS3', 'Node.js', 'Express.js',
            'Django', 'Flask', 'FastAPI', 'Spring Boot', 'Laravel', 'Bootstrap',
            'Tailwind CSS', 'jQuery', 'Webpack', 'Next.js', 'Nuxt.js',
            
            # Databases
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
            'Oracle', 'SQL Server', 'SQLite', 'DynamoDB', 'Cassandra',
            'Neo4j', 'InfluxDB', 'MariaDB',
            
            # Cloud & DevOps
            'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins',
            'Terraform', 'Ansible', 'Git', 'GitLab', 'GitHub Actions',
            'CircleCI', 'Travis CI', 'Helm', 'Istio', 'Prometheus', 'Grafana',
            
            # Data Science & AI
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch',
            'Scikit-learn', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn',
            'Jupyter', 'Apache Spark', 'Hadoop', 'Tableau', 'Power BI',
            'Keras', 'OpenCV', 'NLTK', 'spaCy', 'Computer Vision', 'NLP',
            
            # Mobile Development
            'iOS Development', 'Android Development', 'React Native', 'Flutter',
            'Xamarin', 'Ionic', 'Cordova', 'Unity', 'Unreal Engine',
            
            # Other Technologies
            'Microservices', 'REST API', 'GraphQL', 'gRPC', 'Blockchain',
            'IoT', 'AR/VR', 'Cybersecurity', 'Penetration Testing',
            'Network Security', 'Linux', 'Windows Server', 'Nginx', 'Apache',
            
            # Soft Skills
            'Leadership', 'Communication', 'Problem Solving', 'Teamwork',
            'Project Management', 'Agile', 'Scrum', 'Critical Thinking',
            'Creativity', 'Adaptability', 'Time Management', 'Public Speaking',
            'Negotiation', 'Mentoring', 'Strategic Planning'
        ]
        
        # Job categories with typical required skills
        self.job_categories = {
            'Frontend Developer': [
                'JavaScript', 'React', 'HTML5', 'CSS3', 'TypeScript', 'Vue.js', 'Angular'
            ],
            'Backend Developer': [
                'Python', 'Node.js', 'Java', 'SQL', 'REST API', 'Docker', 'AWS'
            ],
            'Full Stack Developer': [
                'JavaScript', 'React', 'Node.js', 'Python', 'SQL', 'HTML5', 'CSS3', 'Git'
            ],
            'Data Scientist': [
                'Python', 'Machine Learning', 'Pandas', 'NumPy', 'TensorFlow', 'SQL', 'Tableau'
            ],
            'DevOps Engineer': [
                'Docker', 'Kubernetes', 'AWS', 'Jenkins', 'Terraform', 'Linux', 'Git'
            ],
            'Mobile Developer': [
                'React Native', 'Flutter', 'iOS Development', 'Android Development', 'JavaScript'
            ],
            'AI Engineer': [
                'Python', 'TensorFlow', 'PyTorch', 'Machine Learning', 'Deep Learning', 'NLP'
            ],
            'Cloud Architect': [
                'AWS', 'Azure', 'Google Cloud', 'Kubernetes', 'Terraform', 'Microservices'
            ],
            'Security Engineer': [
                'Cybersecurity', 'Penetration Testing', 'Network Security', 'Linux', 'Python'
            ],
            'Product Manager': [
                'Project Management', 'Agile', 'Scrum', 'Leadership', 'Communication', 'Strategic Planning'
            ]
        }
    
    def generate_user_skills(self, job_category=None, skill_overlap=0.7):
        """Generate realistic user skills with some overlap to job requirements"""
        
        if job_category and job_category in self.job_categories:
            required_skills = self.job_categories[job_category]
            
            # User has some of the required skills (based on overlap ratio)
            num_matching = int(len(required_skills) * skill_overlap)
            user_skills = random.sample(required_skills, num_matching)
            
            # Add some additional random skills
            additional_skills = random.sample(
                [skill for skill in self.all_skills if skill not in required_skills],
                random.randint(2, 6)
            )
            user_skills.extend(additional_skills)
            
        else:
            # Random skills for general users
            user_skills = random.sample(self.all_skills, random.randint(5, 12))
        
        return user_skills
    
    def calculate_skill_match_percentage(self, user_skills, required_skills):
        """Calculate percentage match between user skills and job requirements"""
        
        user_skills_set = set(skill.lower().strip() for skill in user_skills)
        required_skills_set = set(skill.lower().strip() for skill in required_skills)
        
        # Calculate exact matches
        exact_matches = len(user_skills_set.intersection(required_skills_set))
        
        # Calculate semantic matches (simplified)
        semantic_matches = 0
        skill_synonyms = {
            'javascript': ['js', 'node.js', 'nodejs'],
            'machine learning': ['ml', 'ai', 'artificial intelligence'],
            'react': ['reactjs', 'react.js'],
            'python': ['py'],
            'sql': ['mysql', 'postgresql', 'database'],
            'aws': ['amazon web services', 'cloud'],
            'docker': ['containerization', 'containers']
        }
        
        for user_skill in user_skills_set:
            for req_skill in required_skills_set:
                if user_skill != req_skill:  # Not exact match
                    # Check synonyms
                    for main_skill, synonyms in skill_synonyms.items():
                        if (user_skill == main_skill and req_skill in synonyms) or \
                           (req_skill == main_skill and user_skill in synonyms) or \
                           (user_skill in synonyms and req_skill in synonyms):
                            semantic_matches += 0.5  # Partial credit for semantic match
                            break
        
        # Calculate total match score
        total_matches = exact_matches + semantic_matches
        max_possible = len(required_skills_set)
        
        if max_possible == 0:
            return 0
        
        percentage = min((total_matches / max_possible) * 100, 100)
        return round(percentage, 1)
    
    def generate_report_data(self, num_users=40):
        """Generate comprehensive report data"""
        
        print(f"🔄 Generating report data for {num_users} users...")
        
        report_data = []
        job_titles = list(self.job_categories.keys())
        
        for i in range(1, num_users + 1):
            # Generate user info
            user_name = self.fake.name()
            user_id = f"USR{i:03d}"
            
            # Random job application
            job_title = random.choice(job_titles)
            required_skills = self.job_categories[job_title]
            
            # Generate user skills with realistic overlap
            overlap_ratio = random.uniform(0.3, 0.9)  # 30% to 90% skill overlap
            user_skills = self.generate_user_skills(job_title, overlap_ratio)
            
            # Calculate matching percentage
            match_percentage = self.calculate_skill_match_percentage(user_skills, required_skills)
            
            # Additional metrics
            total_user_skills = len(user_skills)
            total_required_skills = len(required_skills)
            exact_matches = len(set(user_skills).intersection(set(required_skills)))
            missing_skills = [skill for skill in required_skills if skill not in user_skills]
            
            # Application status based on match percentage
            if match_percentage >= 80:
                status = "Highly Recommended"
                priority = "High"
            elif match_percentage >= 60:
                status = "Good Match"
                priority = "Medium"
            elif match_percentage >= 40:
                status = "Potential Match"
                priority = "Low"
            else:
                status = "Poor Match"
                priority = "Very Low"
            
            # Experience level
            experience_years = random.randint(1, 15)
            if experience_years <= 2:
                experience_level = "Junior"
            elif experience_years <= 5:
                experience_level = "Mid-level"
            elif experience_years <= 10:
                experience_level = "Senior"
            else:
                experience_level = "Expert"
            
            # AI confidence score (simulated)
            ai_confidence = random.randint(75, 99)
            
            # Application date
            app_date = self.fake.date_between(start_date='-30d', end_date='today')
            
            report_data.append({
                'User_ID': user_id,
                'User_Name': user_name,
                'Job_Title': job_title,
                'Experience_Level': experience_level,
                'Experience_Years': experience_years,
                'Extracted_Skills': ', '.join(user_skills),
                'Job_Required_Skills': ', '.join(required_skills),
                'Total_User_Skills': total_user_skills,
                'Total_Required_Skills': total_required_skills,
                'Exact_Matches': exact_matches,
                'Missing_Skills': ', '.join(missing_skills[:5]) + ('...' if len(missing_skills) > 5 else ''),
                'Percentage_Matching': match_percentage,
                'Application_Status': status,
                'Priority': priority,
                'AI_Confidence_Score': ai_confidence,
                'Application_Date': app_date,
                'Skills_Coverage': f"{exact_matches}/{total_required_skills}",
                'Recommendation': self.get_recommendation(match_percentage, experience_years)
            })
        
        print(f"✅ Generated data for {len(report_data)} users")
        return report_data
    
    def get_recommendation(self, match_percentage, experience_years):
        """Generate hiring recommendation"""
        if match_percentage >= 80 and experience_years >= 3:
            return "Strong Hire - Immediate Interview"
        elif match_percentage >= 70 and experience_years >= 2:
            return "Good Candidate - Schedule Interview"
        elif match_percentage >= 60:
            return "Consider - Skills Assessment"
        elif match_percentage >= 40:
            return "Maybe - Training Required"
        else:
            return "Not Recommended"
    
    def create_excel_report(self, data, filename="JobSync_AI_Resume_Analysis_Report.xlsx"):
        """Create comprehensive Excel report with multiple sheets"""
        
        print(f"📊 Creating Excel report: {filename}")
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            
            # Main data sheet
            df_main = pd.DataFrame(data)
            df_main.to_excel(writer, sheet_name='Resume Analysis', index=False)
            
            # Summary statistics sheet
            summary_data = self.create_summary_statistics(data)
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Summary Statistics', index=False)
            
            # Skills analysis sheet
            skills_analysis = self.create_skills_analysis(data)
            df_skills = pd.DataFrame(skills_analysis)
            df_skills.to_excel(writer, sheet_name='Skills Analysis', index=False)
            
            # Job matching analysis
            job_analysis = self.create_job_analysis(data)
            df_jobs = pd.DataFrame(job_analysis)
            df_jobs.to_excel(writer, sheet_name='Job Matching Analysis', index=False)
            
            # Recommendations sheet
            recommendations = self.create_recommendations(data)
            df_recommendations = pd.DataFrame(recommendations)
            df_recommendations.to_excel(writer, sheet_name='Hiring Recommendations', index=False)
        
        print(f"✅ Excel report saved as: {filename}")
        return filename
    
    def create_summary_statistics(self, data):
        """Create summary statistics"""
        df = pd.DataFrame(data)
        
        summary = [
            {'Metric': 'Total Candidates', 'Value': len(data)},
            {'Metric': 'Average Match Percentage', 'Value': f"{df['Percentage_Matching'].mean():.1f}%"},
            {'Metric': 'Highest Match Percentage', 'Value': f"{df['Percentage_Matching'].max():.1f}%"},
            {'Metric': 'Lowest Match Percentage', 'Value': f"{df['Percentage_Matching'].min():.1f}%"},
            {'Metric': 'Candidates with 80%+ Match', 'Value': len(df[df['Percentage_Matching'] >= 80])},
            {'Metric': 'Candidates with 60%+ Match', 'Value': len(df[df['Percentage_Matching'] >= 60])},
            {'Metric': 'Average AI Confidence', 'Value': f"{df['AI_Confidence_Score'].mean():.1f}%"},
            {'Metric': 'Average Experience Years', 'Value': f"{df['Experience_Years'].mean():.1f} years"},
            {'Metric': 'Most Common Job Title', 'Value': df['Job_Title'].mode().iloc[0]},
            {'Metric': 'Average Skills per Candidate', 'Value': f"{df['Total_User_Skills'].mean():.1f}"}
        ]
        
        return summary
    
    def create_skills_analysis(self, data):
        """Analyze skill frequency and demand"""
        all_user_skills = []
        all_required_skills = []
        
        for record in data:
            user_skills = [skill.strip() for skill in record['Extracted_Skills'].split(',')]
            required_skills = [skill.strip() for skill in record['Job_Required_Skills'].split(',')]
            
            all_user_skills.extend(user_skills)
            all_required_skills.extend(required_skills)
        
        from collections import Counter
        
        user_skill_counts = Counter(all_user_skills)
        required_skill_counts = Counter(all_required_skills)
        
        # Top skills analysis
        skills_analysis = []
        
        # Most common user skills
        for i, (skill, count) in enumerate(user_skill_counts.most_common(15), 1):
            demand_count = required_skill_counts.get(skill, 0)
            supply_demand_ratio = count / max(demand_count, 1)
            
            skills_analysis.append({
                'Rank': i,
                'Skill': skill,
                'Candidate_Count': count,
                'Job_Demand': demand_count,
                'Supply_Demand_Ratio': round(supply_demand_ratio, 2),
                'Market_Status': 'Oversupplied' if supply_demand_ratio > 2 else 'Balanced' if supply_demand_ratio > 0.5 else 'In Demand'
            })
        
        return skills_analysis
    
    def create_job_analysis(self, data):
        """Analyze job matching performance"""
        df = pd.DataFrame(data)
        
        job_analysis = []
        for job_title in df['Job_Title'].unique():
            job_data = df[df['Job_Title'] == job_title]
            
            job_analysis.append({
                'Job_Title': job_title,
                'Total_Applicants': len(job_data),
                'Average_Match_Percentage': round(job_data['Percentage_Matching'].mean(), 1),
                'High_Match_Candidates': len(job_data[job_data['Percentage_Matching'] >= 80]),
                'Good_Match_Candidates': len(job_data[job_data['Percentage_Matching'] >= 60]),
                'Average_Experience': round(job_data['Experience_Years'].mean(), 1),
                'Recommended_Hires': len(job_data[job_data['Application_Status'] == 'Highly Recommended']),
                'Competition_Level': 'High' if len(job_data) > 5 else 'Medium' if len(job_data) > 2 else 'Low'
            })
        
        return sorted(job_analysis, key=lambda x: x['Average_Match_Percentage'], reverse=True)
    
    def create_recommendations(self, data):
        """Create hiring recommendations"""
        df = pd.DataFrame(data)
        
        # Top candidates
        top_candidates = df.nlargest(10, 'Percentage_Matching')
        
        recommendations = []
        for _, candidate in top_candidates.iterrows():
            recommendations.append({
                'Rank': len(recommendations) + 1,
                'User_ID': candidate['User_ID'],
                'User_Name': candidate['User_Name'],
                'Job_Title': candidate['Job_Title'],
                'Match_Percentage': candidate['Percentage_Matching'],
                'Experience_Level': candidate['Experience_Level'],
                'Recommendation': candidate['Recommendation'],
                'Key_Strengths': f"Strong in {candidate['Exact_Matches']} required skills",
                'Next_Action': 'Schedule immediate interview' if candidate['Percentage_Matching'] >= 80 else 'Skills assessment recommended'
            })
        
        return recommendations

def main():
    """Generate the Excel report"""
    
    print("🚀 JobSync AI Resume Analysis Report Generator")
    print("=" * 60)
    
    # Initialize generator
    generator = JobSyncReportGenerator()
    
    # Generate data for 40 users
    report_data = generator.generate_report_data(40)
    
    # Create Excel report
    filename = generator.create_excel_report(report_data)
    
    # Display summary
    df = pd.DataFrame(report_data)
    
    print(f"\n📊 REPORT SUMMARY")
    print("=" * 30)
    print(f"Total Users: {len(report_data)}")
    print(f"Average Match: {df['Percentage_Matching'].mean():.1f}%")
    print(f"Best Match: {df['Percentage_Matching'].max():.1f}%")
    print(f"High Matches (80%+): {len(df[df['Percentage_Matching'] >= 80])}")
    print(f"Good Matches (60%+): {len(df[df['Percentage_Matching'] >= 60])}")
    
    print(f"\n📁 Files Created:")
    print(f"✅ {filename}")
    
    print(f"\n🎉 Report generation completed successfully!")
    print(f"Open '{filename}' to view the comprehensive analysis.")

if __name__ == "__main__":
    # Install required packages if not available
    try:
        import pandas as pd
        import openpyxl
    except ImportError:
        import subprocess
        import sys
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "openpyxl"])
        import pandas as pd
        import openpyxl
    
    main()
