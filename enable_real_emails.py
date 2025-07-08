#!/usr/bin/env python3
"""
Quick Email Setup for JobSync
============================

This script enables real email sending for job application confirmations.
Run this to configure your email settings quickly.
"""

def enable_real_emails():
    """Enable real email sending with user input"""
    print("🔧 JobSync Email Setup")
    print("=" * 40)
    print()
    print("This will enable real email sending for job application confirmations.")
    print("Jobseekers will receive actual emails in their Gmail/inbox when they apply for jobs.")
    print()
    
    # Get email credentials
    email = input("Enter your Gmail address: ").strip()
    print()
    print("For Gmail, you need an 'App Password' (not your regular password):")
    print("1. Go to https://myaccount.google.com/apppasswords")
    print("2. Generate an App Password for 'Mail'")
    print("3. Use that 16-character password below")
    print()
    
    import getpass
    password = getpass.getpass("Enter your Gmail App Password: ")
    
    # Update email_config.py
    config_content = f'''#!/usr/bin/env python3
"""
Email Configuration for JobSync - Auto-generated
"""

EMAIL_CONFIG = {{
    'USE_REAL_EMAIL': True,
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 587,
    'MAIL_USE_TLS': True,
    'MAIL_USERNAME': '{email}',
    'MAIL_PASSWORD': '{password}',
}}

def get_email_config():
    return EMAIL_CONFIG
'''
    
    with open('email_config.py', 'w') as f:
        f.write(config_content)
    
    print("\n✅ Email configuration saved!")
    print("🚀 Real emails are now enabled!")
    print()
    print("📧 What happens now:")
    print("- When jobseekers apply for jobs, they'll receive real emails")
    print("- Emails will be sent to their actual Gmail/email addresses")
    print("- Professional HTML emails with application confirmations")
    print()
    print("🧪 To test:")
    print("1. Restart the Flask app: python app.py")
    print("2. Apply for a job as a jobseeker")
    print("3. Check your email for the confirmation")
    print()
    print("📱 The emails will look professional and include:")
    print("- Job title and company name")
    print("- Application confirmation")
    print("- Next steps information")
    print("- Dashboard link")

if __name__ == "__main__":
    try:
        enable_real_emails()
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
