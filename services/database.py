# Import the tools we need to handle files and read/write JSON data structures
import os
import json

# Define the file path where we will store our candidate database records
DB_FILE_PATH = "uploads/candidate_db.json"

def initialize_database():
    """
    This function checks if our JSON database file exists. 
    If it is missing, it creates an empty list and saves it as a new file.
    """
    # Create the uploads folder path directory if it does not exist yet
    os.makedirs(os.path.dirname(DB_FILE_PATH), exist_ok=True)
    
    # If the file is not there, write a blank list [] into it to start fresh
    if not os.path.exists(DB_FILE_PATH):
        with open(DB_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_all_candidates():
    """
    This function reads our local JSON database file and brings back 
    a Python list containing all the stored candidate profiles.
    """
    # Make sure the file exists first
    initialize_database()
    
    try:
        # Open and read the contents of the database file
        with open(DB_FILE_PATH, "r", encoding="utf-8") as f:
            candidates_list = json.load(f)
            return candidates_list
    except Exception as e:
        print(f"Error loading candidate records: {e}")
        return []

def save_candidate_record(candidate_data):
    """
    This function takes a new candidate's data dictionary, loads the existing list, 
    appends the new profile to it, and writes the updated list back to our JSON file.
    """
    # 1. Grab all the current candidates already in our database
    all_candidates = load_all_candidates()
    
    # 2. Add the incoming new candidate profile record to our master list
    all_candidates.append(candidate_data)
    
    # 3. Write the whole updated list back down onto our local system disk file
    try:
        with open(DB_FILE_PATH, "w", encoding="utf-8") as f:
            # indent=4 makes the file look beautifully spaced and readable for humans
            json.dump(all_candidates, f, indent=4)
        return True
    except Exception as e:
        print(f"Failed to save candidate profile record: {e}")
        return False
