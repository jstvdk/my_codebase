import smtplib
from email.mime.text import MIMEText
import os

# Replace these with your details
SENDER_EMAIL = 'coolmuon@gmail.com'  # Your verified sender email
RECEIVER_EMAIL = 'coolmuon@gmail.com'          # Recipient's email
MAILJET_API_KEY = 'REDACTED_MAILJET_API_KEY'          # Mailjet API Key (Public Key)
MAILJET_SECRET_KEY = 'REDACTED_MAILJET_SECRET_KEY'    # Mailjet Secret Key (Private Key)

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