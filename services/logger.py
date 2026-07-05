# Import the tools we need to check folders, handle times, and write files
import os
from datetime import datetime

# Define where we want to save our system log entries
LOGS_FOLDER = "logs"
LOG_FILE_PATH = os.path.join(LOGS_FOLDER, "app.log")

def setup_logger_directory():
    """
    This function checks if the 'logs/' folder exists. 
    If it is missing from the system, it builds it automatically.
    """
    if not os.path.exists(LOGS_FOLDER):
        os.makedirs(LOGS_FOLDER)

def log_event(message, level="INFO"):
    """
    This function writes a single timed diagnostic line down into our log file.
    You can categorize logs by levels like INFO, WARNING, or ERROR.
    """
    # 1. Make sure our log folder directory is ready
    setup_logger_directory()
    
    # 2. Grab the precise time right now to stamp our log entry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 3. Format our clean log text row line entry cleanly
    log_entry = f"[{timestamp}] [{level.upper()}] {message}\n"
    
    try:
        # 4. Open the log file in append mode ('a') so it adds lines instead of overwriting
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        # Fallback print to console if something breaks while writing files
        print(f"Failed to write system log line: {e}")
