import os
import re
import smtplib

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from tkinter import messagebox

from dotenv import load_dotenv
from utils.logger import log_email, log_error


env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    print(f"Warning: .env file not found at {env_path}. Email credentials may not be available.")


def _validate_email(email_address):
    """
    Validate email address format using regex.
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email_address) is not None


def send_mail(receiver_email, output_path, key, loading_window):
    # Validate receiver email
    if not _validate_email(receiver_email):
        if loading_window is not None:
            try:
                loading_window.after(0, loading_window.destroy)
            except Exception:
                loading_window.destroy()
        try:
            if loading_window is not None:
                loading_window.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Invalid email address: {receiver_email}"
                ))
            else:
                messagebox.showerror(
                    "Error",
                    f"Invalid email address: {receiver_email}"
                )
        except Exception:
            pass
        return
    
    sender_email = os.getenv("EMAIL", "").strip()
    smtp_password = os.getenv("APP_PASSWORD", "").strip()

    if not sender_email or not smtp_password:
        if loading_window is not None:
            try:
                loading_window.after(0, loading_window.destroy)
            except Exception:
                loading_window.destroy()
        try:
            if loading_window is not None:
                loading_window.after(0, lambda: messagebox.showerror(
                    "Error",
                    "Email credentials are missing. Please set EMAIL and APP_PASSWORD in the .env file."
                ))
            else:
                messagebox.showerror(
                    "Error",
                    "Email credentials are missing. Please set EMAIL and APP_PASSWORD in the .env file."
                )
        except Exception:
            pass
        return

    subject = "The Key and Encrypted Image"

    message = (
        "The Key for Encrypted Image is:\n\n"
        + key.decode()
    )

    msg = MIMEMultipart()

    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    attachment_name = Path(output_path).name

    with open(output_path, "rb") as attachment:
        part = MIMEApplication(
            attachment.read(),
            Name=attachment_name
        )

        part["Content-Disposition"] = (
            f'attachment; filename="{attachment_name}"'
        )

        msg.attach(part)

    msg.attach(MIMEText(message, "plain"))

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    server = None

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, smtp_password)
        server.send_message(msg)

        if loading_window is not None:
            try:
                loading_window.after(0, loading_window.destroy)
            except Exception:
                loading_window.destroy()

        try:
            if loading_window is not None:
                loading_window.after(0, lambda: messagebox.showinfo(
                    "Success",
                    "Email sent successfully."
                ))
            else:
                messagebox.showinfo(
                    "Success",
                    "Email sent successfully."
                )
        except Exception:
            pass

        log_email()

    except Exception as exc:
        log_error(f"EMAIL failed: {exc}")
        if loading_window is not None:
            try:
                loading_window.after(0, loading_window.destroy)
            except Exception:
                loading_window.destroy()
        try:
            if loading_window is not None:
                loading_window.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Email sending failed: {exc}"
                ))
            else:
                messagebox.showerror(
                    "Error",
                    f"Email sending failed: {exc}"
                )
        except Exception:
            pass

    finally:
        if server is not None:
            try:
                server.quit()
            except Exception:
                pass