import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

# Set these in your shell env or a local .env file (see .env.example)
SENDER_EMAIL = os.environ['SENDER_EMAIL']
RECEIVER_EMAIL = os.environ['RECEIVER_EMAIL']
MAILJET_API_KEY = os.environ['MAILJET_API_KEY']
MAILJET_SECRET_KEY = os.environ['MAILJET_SECRET_KEY']

# Create the email content
subject = 'Test Email from Mailjet'
body = 'Hello, this is a test email sent using Mailjet SMTP relay.'

msg = MIMEText(body)
msg['Subject'] = subject
msg['From'] = SENDER_EMAIL
msg['To'] = RECEIVER_EMAIL

# Set up the SMTP server connection
smtp_server = 'in-v3.mailjet.com'
smtp_port = 587  # Use 465 if you prefer SSL

try:
    # Establish a secure session with Mailjet's SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection using TLS
        server.login(MAILJET_API_KEY, MAILJET_SECRET_KEY)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
    print("Email sent successfully via Mailjet.")
except Exception as e:
    print(f"Failed to send email: {e}")