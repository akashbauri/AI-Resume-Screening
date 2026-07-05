# Import the tools we need to manage paths, operational directories, structured JSON records, and logs
import os
import json
import logging
from datetime import datetime

# Define the new structural production storage file path
DB_FILE_PATH = "data/candidates.json"

# Configure a standard backend production-ready logger instance layout
logger = logging.getLogger("database_service")

def initialize_database():
    """
    This function checks if our target data directory and database file exist.
    If they are missing from the workspace, it builds them safely with an empty list [].
    """
    try:
        # 1. Automatically create the data directory folder if it does not exist
        os.makedirs(os.path.dirname(DB_FILE_PATH), exist_ok=True)
        
        # 2. If the JSON database storage file isn't there, initialize it with a blank array []
        if not os.path.exists(DB_FILE_PATH):
            with open(DB_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Failed to initialize candidate database storage layer: {str(e)}")

def load_candidates():
    """
    This function reads our local JSON database file and returns a Python list containing 
    all candidate profile records. It catches corrupted data files gracefully without crashing.
    """
    initialize_database()
    
    if not os.path.exists(DB_FILE_PATH):
        return []
        
    try:
        with open(DB_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError) as json_err:
        # 4. Handle invalid or corrupted JSON safely by returning an empty list instead of crashing
        logger.error(f"Corrupted database file context detected. Resetting view records. Error: {str(json_err)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected operational failure while reading candidate data file: {str(e)}")
        return []

def _write_database_records(all_candidates):
    """
    Internal helper function to safely commit the Python list records back 
    down onto the storage file using clean indentation and UTF-8 encoding.
    """
    try:
        with open(DB_FILE_PATH, "w", encoding="utf-8") as f:
            # 12. Use indent=4 when saving JSON cleanly structured for human auditing
            json.dump(all_candidates, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logger.error(f"Failed to save candidate records changes onto disk storage file: {str(e)}")
        return False

def get_candidate_by_email(email):
    """
    8. Helper Function: Searches for an applicant profile by their unique email address.
    Returns the candidate dictionary configuration map if located, or None if missing.
    """
    if not email:
        return None
        
    all_candidates = load_candidates()
    target_email_lower = str(email).strip().lower()
    
    for candidate in all_candidates:
        if str(candidate.get("Email", "")).strip().lower() == target_email_lower:
            return candidate
            
    return None

def delete_candidate(email):
    """
    9. Helper Function: Locates an applicant profile matching the email address key 
    and removes it permanently from the local list dataset records on disk.
    Returns True if removed, or False if the profile was not found.
    """
    if not email:
        return False
        
    all_candidates = load_candidates()
    target_email_lower = str(email).strip().lower()
    original_pool_length = len(all_candidates)
    
    # Filter out any list profile entries that match the deletion email criteria
    filtered_candidates = [
        c for c in all_candidates 
        if str(c.get("Email", "")).strip().lower() != target_email_lower
    ]
    
    if len(filtered_candidates) == original_pool_length:
        logger.warning(f"Deletion abandoned: No profile matching target email '{email}' found.")
        return False
        
    return _write_database_records(filtered_candidates)

def save_candidate(candidate_data):
    """
    Saves an applicant's profile schema dictionary record map to the JSON data file.
    If the email already exists, it performs an in-place update while preserving 
    the original Created Time parameters to prevent duplication.
    """
    if not candidate_data or "Email" not in candidate_data:
        logger.error("Save aborted: Profile data dictionary is completely blank or missing primary 'Email' key parameter.")
        return False
        
    all_candidates = load_candidates()
    candidate_email = str(candidate_data.get("Email", "")).strip()
    timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 7. If Status field is missing from pipeline parameters, set it automatically to "New"
    if "Status" not in candidate_data or not candidate_data["Status"]:
        candidate_data["Status"] = "New"
        
    record_index = -1
    for index, candidate in enumerate(all_candidates):
        if str(candidate.get("Email", "")).strip().lower() == candidate_email.lower():
            record_index = index
            break
            
    # 5. If another candidate already exists with the same Email, update instead of creating a duplicate
    if record_index != -1:
        existing_record = all_candidates[record_index]
        
        # Preserve original creation timestamp markers securely
        original_created_time = existing_record.get("Created Time", timestamp_now)
        
        # Merge new attributes over the old record layout parameters
        existing_record.update(candidate_data)
        existing_record["Created Time"] = original_created_time
        existing_record["Updated Time"] = timestamp_now
        
        all_candidates[record_index] = existing_record
        logger.info(f"Successfully synchronized modified fields for existing applicant record: {candidate_email}")
    else:
        # 6. If candidate does not exist, add both Created and Updated timestamps and append new profile item
        candidate_data["Created Time"] = timestamp_now
        candidate_data["Updated Time"] = timestamp_now
        all_candidates.append(candidate_data)
        logger.info(f"Successfully added new candidate profile entry: {candidate_email}")
        
    return _write_database_records(all_candidates)

def update_candidate(email_key, updated_fields):
    """
    Locates an active profile row matching the specific email primary lookup key parameter, 
    and merges the new update payload changes into it. Automatically refreshes Updated Time metrics.
    """
    if not email_key or not updated_fields:
        return False
        
    all_candidates = load_candidates()
    record_found = False
    target_email_lower = str(email_key).strip().lower()
    timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for index, candidate in enumerate(all_candidates):
        if str(candidate.get("Email", "")).strip().lower() == target_email_lower:
            # Capture and lock the profile's original creation history timestamps securely
            original_created_time = candidate.get("Created Time", timestamp_now)
            
            # 10. Update the matching record, automatically refresh time tracking profiles
            all_candidates[index].update(updated_fields)
            all_candidates[index]["Created Time"] = original_created_time
            all_candidates[index]["Updated Time"] = timestamp_now
            record_found = True
            break
            
    if not record_found:
        logger.warning(f"Update failed: No candidate profile entry matching the email target '{email_key}' was found.")
        return False
        
    return _write_database_records(all_candidates)
