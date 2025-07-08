#!/usr/bin/env python3
"""
Complete AI Resume Parser Setup
==============================

This script sets up the complete AI resume parsing system:
1. Installs required dependencies
2. Generates 1200 synthetic resumes
3. Trains the AI model
4. Tests the integration
5. Integrates with JobSync
"""

import subprocess
import sys
import os
import time

def install_requirements():
    """Install required packages"""
    print("📦 Installing AI requirements...")
    
    try:
        # Install spaCy and download English model
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "ai_requirements.txt"])
        
        # Download spaCy English model
        print("📥 Downloading spaCy English model...")
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        
        print("✅ All requirements installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def generate_resume_dataset():
    """Generate synthetic resume dataset"""
    print("\n🏭 Generating synthetic resume dataset...")
    
    try:
        from resume_generator import ResumeGenerator, save_dataset
        
        # Generate resumes
        generator = ResumeGenerator()
        resumes, resume_texts = generator.generate_dataset(1200)
        
        # Save dataset
        save_dataset(resumes, resume_texts)
        
        print("✅ Resume dataset generated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error generating dataset: {e}")
        return False

def train_ai_model():
    """Train the AI resume parser model"""
    print("\n🧠 Training AI resume parser model...")
    
    try:
        # Import and run training
        from train_resume_parser import main as train_main
        train_main()
        
        print("✅ AI model trained successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error training model: {e}")
        return False

def test_integration():
    """Test the AI integration"""
    print("\n🧪 Testing AI integration...")
    
    try:
        from resume_ai_integration import test_resume_parser
        test_resume_parser()
        
        print("✅ Integration test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing integration: {e}")
        return False

def integrate_with_jobsync():
    """Integrate AI parser with JobSync application"""
    print("\n🔗 Integrating with JobSync...")
    
    # Update app.py to include AI resume parsing
    integration_code = '''
# AI Resume Parser Integration
try:
    from resume_ai_integration import JobSyncResumeAI
    ai_resume_parser = JobSyncResumeAI()
    AI_PARSING_ENABLED = True
    print("✅ AI Resume Parser loaded successfully")
except ImportError:
    AI_PARSING_ENABLED = False
    print("⚠️ AI Resume Parser not available - using basic parsing")

def parse_uploaded_resume_ai(file_path):
    """Parse uploaded resume using AI"""
    if AI_PARSING_ENABLED and ai_resume_parser:
        try:
            result = ai_resume_parser.parse_resume_with_ai(file_path)
            return result.get('jobsync_formatted', {})
        except Exception as e:
            print(f"AI parsing error: {e}")
            return {}
    return {}
'''
    
    # Check if app.py exists
    if os.path.exists('app.py'):
        print("📝 Adding AI integration to app.py...")
        
        # Read current app.py
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        # Add integration code if not already present
        if 'AI_PARSING_ENABLED' not in app_content:
            # Find a good place to insert (after imports)
            import_end = app_content.find('app = Flask(__name__)')
            if import_end != -1:
                new_content = (
                    app_content[:import_end] + 
                    integration_code + 
                    '\n\n' + 
                    app_content[import_end:]
                )
                
                # Write updated content
                with open('app.py', 'w') as f:
                    f.write(new_content)
                
                print("✅ AI integration added to app.py")
            else:
                print("⚠️ Could not find insertion point in app.py")
        else:
            print("ℹ️ AI integration already present in app.py")
    else:
        print("⚠️ app.py not found - manual integration required")
    
    return True

def create_demo_script():
    """Create a demo script to showcase the AI parser"""
    
    demo_code = '''#!/usr/bin/env python3
"""
AI Resume Parser Demo
====================
"""

from resume_ai_integration import JobSyncResumeAI
import json

def demo_ai_parser():
    """Demonstrate AI resume parsing capabilities"""
    
    print("🚀 AI Resume Parser Demo")
    print("=" * 40)
    
    # Initialize AI parser
    ai_parser = JobSyncResumeAI()
    
    # Sample resume text
    sample_resume = """
    Sarah Johnson
    Senior Data Scientist
    
    Contact:
    Email: sarah.johnson@email.com
    Phone: (555) 987-6543
    Location: San Francisco, CA
    
    Professional Summary:
    Experienced Data Scientist with 5 years of expertise in machine learning,
    statistical analysis, and data visualization. Proven track record of
    delivering actionable insights from complex datasets.
    
    Technical Skills:
    Python, R, SQL, TensorFlow, PyTorch, Scikit-learn, Pandas, NumPy,
    Matplotlib, Seaborn, Jupyter, Apache Spark, Hadoop, Tableau, Power BI,
    AWS, Docker, Git, Machine Learning, Deep Learning, Natural Language Processing
    
    Work Experience:
    
    Senior Data Scientist | Google | 2021 - Present
    • Led machine learning initiatives for search ranking algorithms
    • Developed predictive models improving user engagement by 15%
    • Mentored junior data scientists and established ML best practices
    
    Data Scientist | Microsoft | 2019 - 2021
    • Built recommendation systems for Azure marketplace
    • Implemented A/B testing frameworks for product optimization
    • Collaborated with engineering teams on model deployment
    
    Junior Data Analyst | Uber | 2018 - 2019
    • Analyzed rider behavior patterns and demand forecasting
    • Created automated reporting dashboards using Python and SQL
    • Supported business decisions with statistical analysis
    
    Education:
    Master of Science in Data Science
    Stanford University, 2018
    GPA: 3.9/4.0
    
    Bachelor of Science in Mathematics
    UC Berkeley, 2016
    GPA: 3.7/4.0
    
    Certifications:
    • AWS Certified Machine Learning - Specialty
    • Google Cloud Professional Data Engineer
    • TensorFlow Developer Certificate
    """
    
    print("📄 Parsing sample resume...")
    
    # Parse with AI
    if ai_parser.parser:
        result = ai_parser.parser.parse_resume(sample_resume)
        enhanced_result = ai_parser.enhance_parse_result(result, sample_resume)
        
        print("\\n🎯 AI Parsing Results:")
        print("=" * 30)
        
        print(f"👤 Name: {enhanced_result.get('name', 'Not detected')}")
        print(f"📧 Email: {enhanced_result.get('email', 'Not detected')}")
        print(f"📱 Phone: {enhanced_result.get('phone', 'Not detected')}")
        
        print(f"\\n🛠️ Skills Detected ({len(enhanced_result.get('skills', []))}):")
        for i, skill in enumerate(enhanced_result.get('skills', [])[:10], 1):
            print(f"  {i}. {skill}")
        if len(enhanced_result.get('skills', [])) > 10:
            print(f"  ... and {len(enhanced_result.get('skills', [])) - 10} more")
        
        print(f"\\n🏢 Companies:")
        for company in enhanced_result.get('companies', []):
            print(f"  • {company}")
        
        print(f"\\n🎓 Education:")
        for edu in enhanced_result.get('education', []):
            print(f"  • {edu}")
        
        print(f"\\n📊 Confidence Score: {enhanced_result.get('confidence_score', 0)}%")
        
        print(f"\\n🔄 JobSync Format:")
        jobsync_data = enhanced_result.get('jobsync_formatted', {})
        for key, value in jobsync_data.items():
            if value:  # Only show non-empty values
                print(f"  {key}: {value}")
    
    else:
        print("❌ AI parser not available")
    
    print("\\n✨ Demo completed!")

if __name__ == "__main__":
    demo_ai_parser()
'''
    
    with open('demo_ai_parser.py', 'w') as f:
        f.write(demo_code)
    
    print("📝 Created demo_ai_parser.py")

def main():
    """Main setup function"""
    
    print("🚀 AI Resume Parser Complete Setup")
    print("=" * 50)
    print("This will set up a complete AI-powered resume parsing system")
    print("for the JobSync application with 1200 training examples.")
    print()
    
    # Confirm setup
    confirm = input("Do you want to proceed? (y/n): ").lower().strip()
    if confirm not in ['y', 'yes']:
        print("Setup cancelled.")
        return
    
    start_time = time.time()
    
    # Step 1: Install requirements
    if not install_requirements():
        print("❌ Setup failed at requirements installation")
        return
    
    # Step 2: Generate dataset
    if not generate_resume_dataset():
        print("❌ Setup failed at dataset generation")
        return
    
    # Step 3: Train model
    if not train_ai_model():
        print("❌ Setup failed at model training")
        return
    
    # Step 4: Test integration
    if not test_integration():
        print("❌ Setup failed at integration testing")
        return
    
    # Step 5: Integrate with JobSync
    integrate_with_jobsync()
    
    # Step 6: Create demo
    create_demo_script()
    
    # Calculate setup time
    setup_time = time.time() - start_time
    
    print(f"\\n🎉 AI Resume Parser Setup Completed!")
    print("=" * 50)
    print(f"⏱️ Total setup time: {setup_time/60:.1f} minutes")
    print()
    print("📋 What was created:")
    print("✅ 1200 synthetic resumes for training")
    print("✅ Trained AI model for resume parsing")
    print("✅ Integration with JobSync application")
    print("✅ Demo script for testing")
    print()
    print("🚀 Next steps:")
    print("1. Run 'python demo_ai_parser.py' to test the AI parser")
    print("2. Restart your JobSync application to use AI parsing")
    print("3. Upload resumes to see automatic skill extraction")
    print()
    print("📊 AI Capabilities:")
    print("• Automatic name, email, phone extraction")
    print("• Intelligent skill detection and categorization")
    print("• Company and job title recognition")
    print("• Education and certification parsing")
    print("• Confidence scoring for parsing quality")
    print("• Seamless integration with JobSync profiles")

if __name__ == "__main__":
    main()
