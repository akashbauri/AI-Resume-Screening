# Import the tools we need to manage paths, files, and timestamps
import os
import json
from datetime import datetime

# Define the file path where we will store our candidate records
DB_FILE_PATH = "uploads/candidate_db.json"

def initialize_database():
    """
    This function checks if our JSON database file exists. 
    If it is missing, it sets up an empty list inside a new file.
    """
    # Create the uploads directory path if it does not exist yet
    os.makedirs(os.path.dirname(DB_FILE_PATH), exist_ok=True)
    
    # If the database file isn't there, initialize it with a blank list []
    if not os.path.exists(DB_FILE_PATH):
        with open(DB_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_candidates():
    """
    This function reads our local JSON database file and returns 
    a Python list containing all the stored candidate profile dictionaries.
    """
    initialize_database()
    try:
        with open(DB_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading candidate records: {e}")
        return []

def save_candidate(candidate_data):
    """
    This function takes a dictionary containing parsed details and matching metrics,
    attaches an automatic creation timestamp, and appends it to our JSON array.
    """
    all_candidates = load_candidates()
    
    # Automatically capture the exact time this entry was recorded in the system
    candidate_data["Created Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Ensure a default 'Status' exists if it wasn't already provided by the pipeline
    if "Status" not in candidate_data:
        candidate_data["Status"] = "Under Review"
        
    all_candidates.append(candidate_data)
    
    try:
        with open(DB_FILE_PATH, "w", encoding="utf-8") as f:
            # indent=4 makes the file structured and cleanly indented for human debugging
            json.dump(all_candidates, f, indent=4)
        return True
    except Exception as e:
        print(f"Failed to append candidate record: {e}")
        return False

def update_candidate(email_key, updated_fields):
    """
    This function looks through the candidate list to locate an entry matching 
    the given unique email address, and merges the new field changes into it.
    """
    all_candidates = load_candidates()
    record_found = False
    
    for index, candidate in enumerate(all_candidates):
        # We use lowercase conversion to avoid matching issues caused by capitalization differences
        if candidate.get("Email", "").lower() == email_key.lower():
            # Update the existing fields with our fresh changes dictionary mapping
            all_candidates[index].update(updated_fields)
            record_found = True
            break
            
    if not record_found:
        print(f"Update failed: No profile matching the email '{email_key}' was found.")
        return False
        
    try:
        with open(DB_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(all_candidates, f, indent=4)
        return True
    except Exception as e:
        print(f"Failed to write candidate adjustments down onto disk storage: {e}")
        return False
