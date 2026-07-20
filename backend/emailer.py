"""
STUDENT NEXT.AI EMAILER
Sends real email via Gmail SMTP -- same mechanism as the Jobsk pattern
this was ported from, just with education-domain templates.

SETUP REQUIRED:
    1. Use a Gmail account (or create one for this app)
    2. https://myaccount.google.com/apppasswords -> generate an App Password
    3. .env:
           EMAIL_ADDRESS=youremail@gmail.com
           EMAIL_PASSWORD=your_16_character_app_password
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")


def _send(to_email, subject, html_body):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print(f"[emailer] Not configured — would have sent '{subject}' to {to_email}")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"[emailer] Sent '{subject}' to {to_email}")
        return True
    except Exception as e:
        print(f"[emailer] Send failed: {e}")
        return False


def send_welcome_email(to_email, name):
    html_body = f"""
    <html><body style="font-family:Arial,sans-serif">
        <h2>Welcome to Student Next.ai, {name}!</h2>
        <p>Set your country, subject interest, and education level to get instant, data-grounded
        university suggestions.</p>
        <p>Upload your transcript in the dashboard to get personalized program matches ranked by relevance.</p>
    </body></html>
    """
    return _send(to_email, "Welcome to Student Next.ai!", html_body)


def send_password_reset_email(to_email, reset_link):
    html_body = f"""
    <html><body style="font-family:Arial,sans-serif;background:#f8fafc;padding:20px">
        <div style="max-width:500px;margin:0 auto;background:white;border-radius:14px;padding:24px">
            <h2 style="color:#6c63ff">Reset your Student Next.ai password</h2>
            <p>Click the link below to set a new password. This link expires in 1 hour.</p>
            <p><a href="{reset_link}" style="color:#6c63ff;font-weight:600">Reset my password →</a></p>
            <p style="color:#999;font-size:12px;margin-top:20px">
                If you didn't request this, you can safely ignore this email.
            </p>
        </div>
    </body></html>
    """
    return _send(to_email, "Reset your Student Next.ai password", html_body)
