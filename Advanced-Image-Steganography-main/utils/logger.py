import os
from datetime import datetime

# Project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Logs folder and file
LOGS_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOGS_DIR, "activity_log.txt")


def initialize_logger():
    """
    Creates the logs folder and log file if they do not exist.
    """
    try:
        os.makedirs(LOGS_DIR, exist_ok=True)

        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w", encoding="utf-8") as file:
                file.write("Timestamp | Operation | Status | Details\n")
                file.write("-" * 90 + "\n")

    except PermissionError:
        print(f"Permission denied: Cannot write to logs directory {LOGS_DIR}")

    except Exception as e:
        print(f"Failed to initialize logger: {str(e)}")


def write_log(operation, status, details=""):
    """
    Writes a log entry.

    Format:
    Timestamp | Operation | Status | Details
    """
    try:
        initialize_logger()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(LOG_FILE, "a", encoding="utf-8") as file:
            file.write(
                f"{timestamp} | "
                f"{operation} | "
                f"{status} | "
                f"{details}\n"
            )

    except (PermissionError, IOError) as e:
        print(f"Failed to write log: {str(e)}")

    except Exception as e:
        print(f"Logging error: {str(e)}")


def log_encode(algorithm="Standard LSB"):
    write_log(
        operation="ENCODE",
        status="SUCCESS",
        details=algorithm
    )


def log_decode(algorithm="Standard LSB"):
    write_log(
        operation="DECODE",
        status="SUCCESS",
        details=algorithm
    )


def log_email():
    write_log(
        operation="EMAIL",
        status="SUCCESS",
        details="Image sent successfully"
    )


def log_error(message):
    """
    Logs user-friendly error messages.
    """
    message_lower = message.lower()

    if any(keyword in message_lower for keyword in [
        "invalid encrypted payload",
        "invalid token",
        "decryption failed",
        "invalid password",
        "incorrect password",
        "wrong steganography algorithm",
        "no hidden message"
    ]):
        friendly_message = (
            "Incorrect password or wrong steganography algorithm selected"
        )
    else:
        friendly_message = message

    write_log(
        operation="ERROR",
        status="FAILED",
        details=friendly_message
    )


def read_logs():
    """
    Reads and returns log entries with error handling.
    """
    try:
        initialize_logger()

        with open(LOG_FILE, "r", encoding="utf-8") as file:
            return file.readlines()

    except (PermissionError, FileNotFoundError, IOError) as e:
        return [f"Error reading logs: {str(e)}\n"]

    except Exception as e:
        return [f"Unexpected error reading logs: {str(e)}\n"]


def clear_logs():
    """
    Clears all log entries with error handling.
    """
    try:
        initialize_logger()

        with open(LOG_FILE, "w", encoding="utf-8") as file:
            file.write("Timestamp | Operation | Status | Details\n")
            file.write("-" * 90 + "\n")

    except (PermissionError, IOError) as e:
        print(f"Failed to clear logs: {str(e)}")

    except Exception as e:
        print(f"Error clearing logs: {str(e)}")