# Import our web interface tools, math table metrics, and database handlers
import streamlit as st
import pandas as pd
from services.database import load_all_candidates, DB_FILE_PATH
import json

def update_candidate_in_json_file(updated_candidate_record):
    """
    This function looks through our database file, finds the matching candidate 
    by their unique email address, replaces their old data details with the new ones, 
    and writes the list back onto the disk.
    """
    try:
        # 1. Open and load our current master list from the database file
        with open(DB_FILE_PATH, "r", encoding="utf-8") as f:
            candidates_list = json.load(f)
            
        # 2. Look at every profile line by line to find the matching email target
        for index, candidate in enumerate(candidates_list):
            if candidate.get("Email") == updated_candidate_record.get("Email"):
                # Replace the old dictionary with our fresh edited data dictionary
                candidates_list[index] = updated_candidate_record
                break
                
        # 3. Write our corrected master list back into the JSON document
        with open(DB_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(candidates_list, f, indent=4)
        return True
    except Exception as e:
        print(f"Error while updating candidate data record: {e}")
        return False


# --- START OF THE WEB UI INTERFACE ---

st.title("📊 Recruiter Action & Review Dashboard")
st.write("Select an applicant profile below to run manual verification assessments, review metrics, edit information, or issue decisions.")

# Fetch our fresh master records list from the database layer
all_candidates = load_all_candidates()

# Check if there are no candidates to manage yet
if not all_candidates:
    st.info("ℹ️ The dashboard is empty because no candidates exist in the database yet. Please go upload a resume file first!")
else:
    # 1. Extract candidate name strings to populate a clean selection dropdown field box
    candidate_options = {c.get("Candidate Name", "Unknown"): c for c in all_candidates}
    
    # Create the dropdown box on screen so the recruiter can pick which candidate to review
    selected_name = st.selectbox("🎯 Choose a candidate profile to review:", list(candidate_options.keys()))
    
    # Isolate the chosen candidate's dictionary map record
    chosen_candidate = candidate_options[selected_name]
    
    st.markdown("---")
    
    # 2. Set up layout columns: Left side displays metrics, right side contains actions form
    left_column, right_column = st.columns([3, 2])
    
    with left_column:
        st.subheader(f"📄 Applicant Profile: {selected_name}")
        
        # Display core match analytics inside colored metric display counters
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            score_val = chosen_candidate.get("Score", 0)
            st.metric("AI Match Fit Score", f"{score_val}%")
        with m_col2:
            current_state = chosen_candidate.get("Status", "Under Review")
            st.metric("Application Review Status", current_state)
            
        # Display structural data fields cleanly using styled bold text rows
        st.write(f"**📧 Email Address:** {chosen_candidate.get('Email', 'N/A')}")
        st.write(f"**📞 Contact Number:** {chosen_candidate.get('Phone', 'N/A')}")
        st.write(f"**🤝 Recommendation Action:** {chosen_candidate.get('Recommendation', 'N/A')}")
        
        # Pull out skills lists and format them as clear text tags
        candidate_skills = chosen_candidate.get("Skills", [])
        if isinstance(candidate_skills, list):
            skills_string = ", ".join(candidate_skills)
        else:
            skills_string = str(candidate_skills)
        st.write(f"**🛠️ Extracted Competency Skills:** {skills_string}")
        
        # Display the custom recruiter review notebook logs if they exist
        st.markdown("##### 📝 Recruiter Assessment Log Notes:")
        existing_notes = chosen_candidate.get("Notes", "No notes recorded yet for this profile candidate.")
        st.info(existing_notes)
        
    with right_column:
        st.subheader("⚙️ Management Evaluation Panel")
        
        # Wrap our input change selectors inside a sub-form block structure
        with st.form("recruiter_action_form", clear_on_submit=False):
            
            st.markdown("**1. Modify Candidate Profile Fields:**")
            # Editable inputs pre-filled with the candidate's existing record details
            new_name = st.text_input("Candidate Name Name:", value=chosen_candidate.get("Candidate Name", ""))
            new_phone = st.text_input("Contact Phone Line:", value=chosen_candidate.get("Phone", ""))
            
            st.markdown("**2. Update Recruitment Review State Status:**")
            # Dropdown menu to switch between custom action workflow stages
            new_status = st.selectbox(
                "Select Next Stage Action Decision:",
                ["Under Review", "Manual Review Required", "Approved for Interview", "Rejected / Archive"],
                index=["Under Review", "Manual Review Required", "Approved for Interview", "Rejected / Archive"].index(current_state) if current_state in ["Under Review", "Manual Review Required", "Approved for Interview", "Rejected / Archive"] else 0
            )
            
            st.markdown("**3. Add Log Assessment Notes:**")
            # Text layout area to add interview comments or profile feedback details
            new_notes_input = st.text_area("Append evaluation diary entries:", placeholder="Add candidate screening feedback or interview scheduling remarks here...")
            
            # Submit action button triggers form calculations execution
            save_button = st.form_submit_button("Save Update Logs")
            
            if save_button:
                # Compile updated data details back into the candidate's core profile record structure
                chosen_candidate["Candidate Name"] = new_name
                chosen_candidate["Phone"] = new_phone
                chosen_candidate["Status"] = new_status
                
                # Append fresh comment logs onto historical text details logs safely
                if new_notes_input.strip() != "":
                    old_notes_log = chosen_candidate.get("Notes", "")
                    if old_notes_log and old_notes_log != "No notes recorded yet for this profile candidate.":
                        chosen_candidate["Notes"] = old_notes_log + "\n" + new_notes_input.strip()
                    else:
                        chosen_candidate["Notes"] = new_notes_input.strip()
                
                # Commit everything securely into our JSON file using our top helper function
                success_flag = update_candidate_in_json_file(chosen_candidate)
                
                if success_flag:
                    st.success("🎉 Candidate profile records saved successfully! Refreshing dashboard data layout view...")
                    # Force Streamlit to rerender and instantly show updated values on screen
                    st.rerun()
                else:
                    st.error("❌ An issue occurred while attempting to write adjustments down onto database disk storage.")
