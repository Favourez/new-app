#!/usr/bin/env python3
"""
Resume AI Integration for JobSync
================================

This script integrates the trained AI resume parser with the JobSync application
for automatic skill extraction and profile completion.
"""

import os
import sys
import json
import pdfplumber
import docx
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from train_resume_parser import ResumeParser
except ImportError:
    print("❌ ResumeParser not found. Please run training first.")
    ResumeParser = None

class JobSyncResumeAI:
    """AI-powered resume parser for JobSync application"""
    
    def __init__(self):
        self.parser = None
        self.initialize_parser()
    
    def initialize_parser(self):
        """Initialize the trained AI parser"""
        try:
            if ResumeParser:
                self.parser = ResumeParser()
                print("✅ AI Resume Parser initialized successfully")
            else:
                print("❌ AI Parser not available - using fallback methods")
        except Exception as e:
            print(f"⚠️ Error initializing AI parser: {e}")
            print("Using fallback parsing methods")
    
    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF file"""
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path):
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting DOCX text: {e}")
            return ""
    
    def extract_text_from_file(self, file_path):
        """Extract text from various file formats"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return ""
        
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        elif file_extension == '.txt':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading text file: {e}")
                return ""
        else:
            print(f"Unsupported file format: {file_extension}")
            return ""
    
    def parse_resume_with_ai(self, file_path):
        """Parse resume using trained AI model"""
        
        # Extract text from file
        text = self.extract_text_from_file(file_path)
        
        if not text:
            return self.fallback_parse_result()
        
        # Use AI parser if available
        if self.parser:
            try:
                result = self.parser.parse_resume(text)
                
                # Post-process and enhance results
                enhanced_result = self.enhance_parse_result(result, text)
                return enhanced_result
                
            except Exception as e:
                print(f"AI parsing error: {e}")
                return self.fallback_parse_from_text(text)
        else:
            # Use fallback parsing
            return self.fallback_parse_from_text(text)
    
    def enhance_parse_result(self, ai_result, original_text):
        """Enhance AI parsing results with additional processing"""
        
        enhanced = ai_result.copy()
        
        # Clean and deduplicate skills
        if 'skills' in enhanced:
            enhanced['skills'] = self.clean_skills_list(enhanced['skills'])
        
        # Extract additional information using regex
        additional_info = self.extract_additional_info(original_text)
        
        # Merge additional information
        for key, value in additional_info.items():
            if key not in enhanced or not enhanced[key]:
                enhanced[key] = value
        
        # Calculate confidence score
        enhanced['confidence_score'] = self.calculate_confidence_score(enhanced, original_text)
        
        # Format for JobSync compatibility
        enhanced['jobsync_formatted'] = self.format_for_jobsync(enhanced)
        
        return enhanced
    
    def clean_skills_list(self, skills):
        """Clean and deduplicate skills list"""
        if not skills:
            return []
        
        # Remove duplicates and clean
        cleaned_skills = []
        seen = set()
        
        for skill in skills:
            skill_clean = skill.strip().title()
            skill_lower = skill_clean.lower()
            
            # Skip if already seen or too short
            if skill_lower in seen or len(skill_clean) < 2:
                continue
            
            # Skip common words that aren't skills
            skip_words = {'and', 'or', 'the', 'with', 'for', 'in', 'at', 'on', 'to', 'of'}
            if skill_lower in skip_words:
                continue
            
            cleaned_skills.append(skill_clean)
            seen.add(skill_lower)
        
        return cleaned_skills[:20]  # Limit to top 20 skills
    
    def extract_additional_info(self, text):
        """Extract additional information using regex patterns"""
        import re
        
        additional = {}
        
        # Extract email if not found
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            additional['email'] = emails[0]
        
        # Extract phone if not found
        phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
        phones = re.findall(phone_pattern, text)
        if phones:
            additional['phone'] = f"({phones[0][0]}) {phones[0][1]}-{phones[0][2]}"
        
        # Extract years of experience
        exp_pattern = r'(\d+)[\+]?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)'
        exp_matches = re.findall(exp_pattern, text, re.IGNORECASE)
        if exp_matches:
            additional['years_experience'] = max([int(x) for x in exp_matches])
        
        # Extract degree information
        degree_pattern = r'(Bachelor|Master|PhD|B\.S\.|M\.S\.|B\.A\.|M\.A\.).*?(?:in\s+)?([A-Za-z\s]+?)(?:\s|,|\.|\n)'
        degree_matches = re.findall(degree_pattern, text, re.IGNORECASE)
        if degree_matches:
            additional['degree'] = f"{degree_matches[0][0]} in {degree_matches[0][1].strip()}"
        
        return additional
    
    def calculate_confidence_score(self, result, text):
        """Calculate confidence score for parsing results"""
        
        score = 0
        max_score = 100
        
        # Check if key fields are found
        if result.get('name'):
            score += 20
        if result.get('email'):
            score += 15
        if result.get('phone'):
            score += 10
        if result.get('skills') and len(result['skills']) > 0:
            score += 25
        if result.get('companies') and len(result['companies']) > 0:
            score += 15
        if result.get('education') or result.get('universities'):
            score += 15
        
        return min(score, max_score)
    
    def format_for_jobsync(self, result):
        """Format parsing results for JobSync application"""
        
        formatted = {
            'name': result.get('name', ''),
            'email': result.get('email', ''),
            'phone': result.get('phone', ''),
            'skills': ', '.join(result.get('skills', [])),
            'experience': f"{result.get('years_experience', 0)} years experience" if result.get('years_experience') else '',
            'education': result.get('degree', ''),
            'companies': ', '.join(result.get('companies', [])),
            'job_titles': ', '.join(result.get('job_titles', [])),
            'parsing_confidence': result.get('confidence_score', 0)
        }
        
        return formatted
    
    def fallback_parse_from_text(self, text):
        """Fallback parsing when AI is not available"""
        import re
        
        result = {
            'name': '',
            'email': '',
            'phone': '',
            'skills': [],
            'companies': [],
            'job_titles': [],
            'education': [],
            'universities': [],
            'confidence_score': 30  # Lower confidence for fallback
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            result['email'] = emails[0]
        
        # Extract phone
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, text)
        if phones:
            result['phone'] = phones[0]
        
        # Extract potential skills (basic keyword matching)
        common_skills = [
            'Python', 'JavaScript', 'Java', 'React', 'Angular', 'Node.js',
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'AWS', 'Docker',
            'Git', 'Linux', 'HTML', 'CSS', 'PHP', 'C++', 'C#'
        ]
        
        found_skills = []
        text_lower = text.lower()
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        result['skills'] = found_skills
        
        # Format for JobSync
        result['jobsync_formatted'] = self.format_for_jobsync(result)
        
        return result
    
    def fallback_parse_result(self):
        """Return empty result when parsing fails"""
        return {
            'name': '',
            'email': '',
            'phone': '',
            'skills': [],
            'companies': [],
            'job_titles': [],
            'education': [],
            'universities': [],
            'confidence_score': 0,
            'error': 'Could not extract text from file',
            'jobsync_formatted': {
                'name': '',
                'email': '',
                'phone': '',
                'skills': '',
                'experience': '',
                'education': '',
                'companies': '',
                'job_titles': '',
                'parsing_confidence': 0
            }
        }

def integrate_with_jobsync():
    """Integration function for JobSync application"""
    
    # This function can be imported and used in app.py
    def parse_uploaded_resume(file_path):
        """Parse uploaded resume and return structured data"""
        
        ai_parser = JobSyncResumeAI()
        result = ai_parser.parse_resume_with_ai(file_path)
        
        return result.get('jobsync_formatted', {})
    
    return parse_uploaded_resume

def test_resume_parser():
    """Test the resume parser with sample files"""
    
    print("🧪 Testing Resume AI Parser")
    print("=" * 40)
    
    # Initialize parser
    ai_parser = JobSyncResumeAI()
    
    # Test with sample text
    sample_resume = """
    John Doe
    Software Engineer
    
    Email: john.doe@email.com
    Phone: (555) 123-4567
    
    Skills: Python, JavaScript, React, Node.js, SQL, AWS, Docker
    
    Experience:
    Senior Software Engineer at Google (2020-Present)
    Software Developer at Microsoft (2018-2020)
    
    Education:
    Bachelor of Science in Computer Science
    Stanford University, 2018
    """
    
    print("📄 Parsing sample resume...")
    result = ai_parser.parser.parse_resume(sample_resume) if ai_parser.parser else ai_parser.fallback_parse_from_text(sample_resume)
    
    print("\n📊 Parsing Results:")
    print(f"Name: {result.get('name', 'Not found')}")
    print(f"Email: {result.get('email', 'Not found')}")
    print(f"Phone: {result.get('phone', 'Not found')}")
    print(f"Skills: {result.get('skills', [])}")
    print(f"Companies: {result.get('companies', [])}")
    print(f"Confidence: {result.get('confidence_score', 0)}%")
    
    if 'jobsync_formatted' in result:
        print(f"\n🔄 JobSync Format:")
        for key, value in result['jobsync_formatted'].items():
            print(f"  {key}: {value}")

def main():
    """Main function for testing"""
    
    print("🚀 JobSync Resume AI Integration")
    print("=" * 50)
    
    # Check if model exists
    if os.path.exists("resume_parser_model"):
        print("✅ Trained model found")
        test_resume_parser()
    else:
        print("❌ Trained model not found")
        print("Please run the following commands first:")
        print("1. python resume_generator.py")
        print("2. python train_resume_parser.py")
        print("\nThen run this script again to test the integration.")

if __name__ == "__main__":
    main()
