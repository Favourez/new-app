# 📧 Email Setup Instructions for JobSync

## Quick Setup

To enable real email sending for the "Forgot Password" feature, follow these steps:

### Option 1: Automatic Setup (Recommended)
```bash
python setup_email.py
```
This interactive script will guide you through the email configuration.

### Option 2: Manual Setup
Edit the `email_config.py` file and update the following:

```python
EMAIL_CONFIG = {
    'USE_REAL_EMAIL': True,  # Change to True
    'MAIL_USERNAME': 'your-email@gmail.com',  # Your email
    'MAIL_PASSWORD': 'your-app-password',     # Your app password
}
```

## Gmail Setup (Most Common)

### Step 1: Enable 2-Factor Authentication
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Turn on **2-Step Verification**

### Step 2: Generate App Password
1. Go to [App Passwords](https://myaccount.google.com/apppasswords)
2. Select **Mail** and your device
3. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

### Step 3: Configure JobSync
1. Run `python setup_email.py`
2. Choose Gmail
3. Enter your email: `your-email@gmail.com`
4. Enter the 16-character app password (not your regular password)

## Other Email Providers

### Outlook/Hotmail
- SMTP Server: `smtp-mail.outlook.com`
- Port: `587`
- Use your regular email and password

### Yahoo Mail
- SMTP Server: `smtp.mail.yahoo.com`
- Port: `587`
- You may need to enable "Less secure app access"

### Custom SMTP
- Configure your own SMTP server settings
- Contact your email provider for SMTP details

## Testing

After setup:
1. Restart the Flask application: `python app.py`
2. Go to login page: `http://127.0.0.1:8080/login`
3. Click "Forgot your password?"
4. Enter your email address
5. Check your email for reset instructions

## Troubleshooting

### Common Issues:

**"Authentication failed"**
- For Gmail: Make sure you're using App Password, not regular password
- For Gmail: Ensure 2FA is enabled
- Check email and password are correct

**"Connection refused"**
- Check your internet connection
- Verify SMTP server and port
- Check firewall/antivirus settings

**"No email received"**
- Check spam/junk folder
- Verify email address is correct
- Check email logs: `http://127.0.0.1:8080/email_log`

**"SSL/TLS errors"**
- Ensure TLS is enabled in configuration
- Try port 465 with SSL instead of 587 with TLS

### Demo Mode
If you don't want to set up real email:
- Keep `USE_REAL_EMAIL: False` in `email_config.py`
- Emails will be logged to console and `email_log.txt`
- View emails at: `http://127.0.0.1:8080/email_log`

## Security Notes

⚠️ **Important Security Guidelines:**

1. **Never commit real credentials to version control**
2. **Use App Passwords for Gmail, not your main password**
3. **Keep your email credentials secure**
4. **Consider using environment variables in production**

## Production Deployment

For production, consider using:
- **SendGrid** - Professional email service
- **Mailgun** - Reliable email API
- **Amazon SES** - AWS email service
- **Environment variables** for credentials

Example with environment variables:
```python
import os
EMAIL_CONFIG = {
    'USE_REAL_EMAIL': True,
    'MAIL_USERNAME': os.getenv('MAIL_USERNAME'),
    'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD'),
}
```

## Support

If you need help:
1. Check the troubleshooting section above
2. Verify your email provider's SMTP settings
3. Test with a simple email client first
4. Check the Flask application logs for error messages

---

**Ready to test?** Run `python setup_email.py` to get started! 🚀
