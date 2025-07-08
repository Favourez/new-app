#!/usr/bin/env python3
"""
Test Job Application Email System
=================================

This script tests the job application email confirmation system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import send_application_confirmation_email
from email_config import get_email_config

def test_application_email():
    """Test sending a job application confirmation email"""
    print("🧪 Testing Job Application Email System")
    print("=" * 50)
    
    # Check email configuration
    config = get_email_config()
    if not config.get('USE_REAL_EMAIL', False):
        print("❌ Real email is not enabled.")
        print("Run 'python enable_real_emails.py' first to set up email.")
        return
    
    print("✅ Real email is enabled")
    print(f"📧 Using email: {config['MAIL_USERNAME']}")
    print()
    
    # Get test email address
    test_email = input("Enter email address to test (your email): ").strip()
    if not test_email:
        print("❌ No email address provided.")
        return
    
    print(f"\n📤 Sending test application confirmation email to: {test_email}")
    print("⏳ Please wait...")
    
    # Send test email
    success = send_application_confirmation_email(
        applicant_email=test_email,
        applicant_name="Test User",
        job_title="Senior Software Developer",
        company_name="Tech Innovations Inc."
    )
    
    if success:
        print("\n✅ Test email sent successfully!")
        print("📧 Check your email inbox for the application confirmation.")
        print()
        print("📱 The email should include:")
        print("- Professional HTML formatting")
        print("- Job application confirmation")
        print("- Application details")
        print("- Next steps information")
        print("- Dashboard link")
        print()
        print("🎉 Job application emails are working!")
    else:
        print("\n❌ Failed to send test email.")
        print("Check your email configuration and try again.")

if __name__ == "__main__":
    try:
        test_application_email()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure you've run 'python enable_real_emails.py' first.")
