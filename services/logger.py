# Import the tools we need to check folders, track processing durations, and format timestamps
import os
import time
from datetime import datetime

# Define where we want to save our system log entries
LOGS_FOLDER = "logs"
LOG_FILE_PATH = os.path.join(LOGS_FOLDER, "app.log")

def setup_logger_directory():
    """
    This function checks if the 'logs/' folder exists. 
    If it is missing from the system workspace, it builds it automatically.
    """
    if not os.path.exists(LOGS_FOLDER):
        os.makedirs(LOGS_FOLDER, exist_ok=True)

def log_event(category, message, level="INFO", processing_time_ms=None):
    """
    This is the core production logging engine. It categorizes events into 
    specific system actions (Uploads, AI Requests, Errors, Database, etc.) 
    and appends a beautifully structured tracking row entry to the disk.
    
    Parameters:
    - category (str): The type of system action (e.g., "UPLOAD", "AI_REQUEST", "ERROR", "DATABASE")
    - message (str): Clear descriptive text explaining the event
    - level (str): Log severity level (e.g., "INFO", "WARNING", "ERROR")
    - processing_time_ms (float): Optional duration value to record task speeds
    """
    # 1. Make sure our log storage directory layout is ready on the disk
    setup_logger_directory()
    
    # 2. Grab the precise current time to timestamp our event entry tracking line
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 3. Format the execution speed text suffix if processing time parameter was passed
    duration_suffix = f" [Duration: {processing_time_ms:.2f}ms]" if processing_time_ms is not None else ""
    
    # 4. Construct a clear, standardized log trace row line structure
    log_entry = f"[{timestamp}] [{level.upper()}] [{category.upper()}] {message}{duration_suffix}\n"
    
    try:
        # 5. Open the target log file in append ('a') mode to safely append text rows without data erasure
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        # Fallback console print trace if local file locks or disk write access issues emerge
        print(f"CRITICAL: Failed to write system trace entry down to log file. Error: {e}")

# --- REUSABLE QUICK INTEGRATION HELPER FUNCTIONS ---

def log_upload(filename, size_kb):
    """Logs resume or job description upload actions."""
    log_event(category="UPLOAD", message=f"File successfully received: '{filename}' (Size: {size_kb:.2f} KB)", level="INFO")

def log_ai_request(model_name, action_type, start_time):
    """Calculates model request latency and logs details about Groq AI interactions."""
    duration_ms = (time.time() - start_time) * 1000
    log_event(category="AI_REQUEST", message=f"Inference completed for action '{action_type}' using model '{model_name}'", level="INFO", processing_time_ms=duration_ms)

def log_database_action(action_type, details):
    """Logs records management interactions (Save, Load, Update) across the JSON database storage layer."""
    log_event(category="DATABASE", message=f"Database operational event [{action_type}] executed: {details}", level="INFO")

def log_system_error(module_name, error_message):
    """Logs runtime execution errors, exceptions, or connection failures securely for diagnostic checks."""
    log_event(category="ERROR", message=f"Exception caught in module '{module_name}': {error_message}", level="ERROR")
