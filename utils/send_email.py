import os
import smtplib
from email.message import EmailMessage
import hashlib
import random
from dotenv import load_dotenv


load_dotenv()
sender_email = os.environ.get("EMAIL")
app_password = os.environ.get("APP_PASSWORD")


def _generate_otp():
    return str(random.randint(100000, 999999))


def _hash_otp(otp):
    return hashlib.sha256(otp.encode("utf-8")).hexdigest()


def send_otp_email(email, subject="Your E-Commerce OTP", message_template=None):
    try:
        receiver_email = email.strip()
        otp = _generate_otp()

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = receiver_email

        if message_template:
            msg.set_content(message_template.format(otp=otp))
        else:
            msg.set_content(f"Your OTP for E-Commerce Registration is: {otp}")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)

        print("OTP sent successfully!")
        return _hash_otp(otp), otp

    except Exception as e:
        print("Failed to send email:", e)
        return None, None


def verify_otp(otp_input, otp_hash):
    if not otp_input or not otp_hash:
        return False
    return _hash_otp(otp_input) == otp_hash