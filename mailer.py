import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM", MAIL_USERNAME)
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:5000")


def mail_is_configured():
    return bool(MAIL_USERNAME and MAIL_PASSWORD)


def send_password_reset_email(to_email, reset_link):
    """
    Sends a password-reset email with the given link.

    If MAIL_USERNAME / MAIL_PASSWORD are not set in .env, no real email
    is sent -- instead the link is printed to the console so the
    reset flow can still be tested locally without an SMTP setup.
    Returns True if an email was actually sent, False if it fell
    back to the console.
    """

    if not mail_is_configured():

        print("=" * 60)
        print("PASSWORD RESET (no MAIL_USERNAME/MAIL_PASSWORD configured)")
        print(f"To: {to_email}")
        print(f"Reset link: {reset_link}")
        print("=" * 60)

        return False

    subject = "Reset your Career Companion password"

    body = (
        "We received a request to reset your Career Companion password.\n\n"
        f"Click the link below to choose a new password. This link expires "
        "in 30 minutes and can only be used once.\n\n"
        f"{reset_link}\n\n"
        "If you didn't request this, you can safely ignore this email."
    )

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = MAIL_FROM
    message["To"] = to_email

    with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:

        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_FROM, [to_email], message.as_string())

    return True
