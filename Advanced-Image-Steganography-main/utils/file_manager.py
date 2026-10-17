from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"
TEMP_DIR = BASE_DIR / "temp"


def ensure_directories():
    """
    Create required folders if they do not already exist.
    """
    for folder in (OUTPUT_DIR, LOGS_DIR, TEMP_DIR):
        folder.mkdir(parents=True, exist_ok=True)


def get_output_directory():
    """
    Return the output folder path.
    """
    return OUTPUT_DIR


def get_logs_directory():
    """
    Return the logs folder path.
    """
    return LOGS_DIR


def get_temp_directory():
    """
    Return the temp folder path.
    """
    return TEMP_DIR


def generate_output_filename(original_file=None):
    """
    Generate a unique filename for the encoded image.
    Uses microsecond timestamp to minimize collision risk.
    """
    ensure_directories()

    original_path = Path(original_file) if original_file else None
    name = original_path.stem if original_path else "IMG"
    extension = original_path.suffix if original_path and original_path.suffix else ".png"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # Added microseconds
    candidate = OUTPUT_DIR / f"{name}_encoded_{timestamp}{extension}"
    counter = 1

    # Safety check: prevent infinite loops in edge case
    max_attempts = 1000
    while candidate.exists() and counter < max_attempts:
        candidate = OUTPUT_DIR / f"{name}_encoded_{timestamp}_{counter}{extension}"
        counter += 1

    if counter >= max_attempts:
        raise RuntimeError("Failed to generate unique filename after 1000 attempts.")

    return str(candidate)


def validate_file_path(file_path):
    """
    Check whether the given file exists and is a regular file.
    """
    if not file_path:
        return False

    return Path(file_path).is_file()