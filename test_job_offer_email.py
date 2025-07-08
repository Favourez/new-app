#!/usr/bin/env python3
"""
Test Job Offer Email System
===========================

This script tests the job offer email functionality by simulating an employer
accepting a job application and sending a real email to the candidate.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import send_job_offer_email, send_rejection_email

def test_job_offer_email():
    """Test sending a job offer email"""
    print("🧪 Testing Job Offer Email System")
    print("=" * 50)
    
    # Create a mock application object
    mock_application = {
        'candidate_email': 'falanaspectrum@gmail.com',  # Test email
        'candidate_name': 'John Doe',
        'job_title': 'Senior Python Developer',
        'company_name': 'Tech Innovations Inc.',
        'salary': 'CFA 900,000 - CFA 1,200,000',
        'location': 'Yaoundé, Cameroon',
        'job_type': 'full-time'
    }
    
    print("📧 Sending job offer email...")
    print(f"To: {mock_application['candidate_email']}")
    print(f"Position: {mock_application['job_title']}")
    print(f"Company: {mock_application['company_name']}")
    print()
    
    # Send job offer email
    success = send_job_offer_email(mock_application)
    
    if success:
        print("✅ Job offer email sent successfully!")
        print("📧 Check the email inbox for the job offer notification.")
        print()
        print("📱 The email includes:")
        print("- Congratulations message")
        print("- Job offer details (position, salary, location)")
        print("- Why the candidate was chosen")
        print("- Next steps for the hiring process")
        print("- Professional HTML formatting")
    else:
        print("❌ Failed to send job offer email.")
        print("Check your email configuration and try again.")

def test_rejection_email():
    """Test sending a rejection email"""
    print("\n🧪 Testing Rejection Email System")
    print("=" * 50)
    
    # Create a mock application object
    mock_application = {
        'candidate_email': 'falanaspectrum@gmail.com',  # Test email
        'candidate_name': 'Jane Smith',
        'job_title': 'Frontend Developer',
        'company_name': 'Digital Solutions Ltd.',
        'employer_name': 'Digital Solutions Ltd.'
    }
    
    print("📧 Sending rejection email...")
    print(f"To: {mock_application['candidate_email']}")
    print(f"Position: {mock_application['job_title']}")
    print(f"Company: {mock_application['company_name']}")
    print()
    
    # Send rejection email
    success = send_rejection_email(mock_application)
    
    if success:
        print("✅ Rejection email sent successfully!")
        print("📧 Check the email inbox for the application update.")
        print()
        print("📱 The email includes:")
        print("- Professional rejection message")
        print("- Encouragement to keep applying")
        print("- Future opportunities mention")
        print("- Link to continue job search")
        print("- Respectful and supportive tone")
    else:
        print("❌ Failed to send rejection email.")
        print("Check your email configuration and try again.")

def main():
    """Main function to test both email types"""
    print("🚀 JobSync Email Notification Testing")
    print("=" * 60)
    print()
    
    try:
        # Test job offer email
        test_job_offer_email()
        
        # Ask if user wants to test rejection email too
        print("\n" + "=" * 60)
        test_rejection = input("Do you want to test rejection email too? (y/n): ").lower().strip()
        
        if test_rejection in ['y', 'yes']:
            test_rejection_email()
        
        print("\n🎉 Email testing completed!")
        print("📧 Check your email inbox for the notifications.")
        print()
        print("🔧 How it works in the application:")
        print("1. Employer logs in to dashboard")
        print("2. Views applications for their jobs")
        print("3. Clicks Accept ✅ or Reject ❌ button")
        print("4. System automatically sends appropriate email")
        print("5. Candidate receives professional notification")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        print("Make sure the Flask app is running and email is configured.")

if __name__ == "__main__":
    main()
