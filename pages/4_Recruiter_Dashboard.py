# Import our web interface components, dropdown matrices, and the updated database service
import streamlit as st
from services.database import load_candidates, update_candidate

# Set page layout to wide for a clear side-by-side split action board
st.set_page_layout = "wide"

st.title("📊 Recruiter Action & Review Dashboard")
st.write("Select an applicant profile below to run manual verification assessments, edit information, or issue decisions.")

# Fetch our fresh master records list from the database layer
all_candidates = load_candidates()

# Check if there are no candidates to manage yet
if not all_candidates:
    st.info("ℹ️ The dashboard is empty because no candidates exist in the database yet. Please go upload a resume file first!")
else:
    # 1. Extract candidate name strings to populate a clean selection dropdown field box
    # We map "Name (Email)" to ensure uniqueness if two applicants share the same name
    candidate_map = {f"{c.get('Candidate Name', 'Unknown')} ({c.get('Email', 'N/A')})": c for c in all_candidates}
    
    # Create the selection dropdown box on screen
    selected_key = st.selectbox("🎯 Choose a candidate profile to manage:", list(candidate_map.keys()))
    
    # Isolate the chosen candidate's dictionary data records map
    chosen_candidate = candidate_map[selected_key]
    candidate_email = chosen_candidate.get("Email", "")
    
    st.markdown("---")
    
    # 2. Set up layout columns: Left side displays data metrics, right side contains updates form
    left_column, right_column = st.columns([3, 2])
    
    with left_column:
        st.subheader(f"📄 Applicant Profile: {chosen_candidate.get('Candidate Name', 'Unknown')}")
        
        # Display core match analytics inside colored metric display counters
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            score_val = chosen_candidate.get("Match Score", 0)
            st.metric("AI Match Fit Score", f"{score_val}%")
        with m_col2:
            current_rec = chosen_candidate.get("Recommendation", "N/A")
            st.metric("AI Recommendation", current_rec)
        with m_col3:
            current_state = chosen_candidate.get("Status", "Under Review")
            st.metric("Processing Status", current_state)
            
        # Display structural candidate data fields cleanly
        st.markdown("##### 🗂️ Core Information Details")
        st.write(f"**📧 Email Address:** {candidate_email}")
        st.write(f"**📞 Contact Number:** {chosen_candidate.get('Phone', 'N/A')}")
        st.write(f"**📍 Current Location:** {chosen_candidate.get('Location', 'N/A')}")
        st.write(f"**💼 Current Role:** {chosen_candidate.get('Current Role', 'N/A')} at {chosen_candidate.get('Company', 'N/A')}")
        
        # Display historical text details logs safely
        st.markdown("##### 📝 Summary Assessment")
        st.info(chosen_candidate.get("Summary", "No automated summary evaluation notes recorded for this applicant profile."))
        
        # Display custom recruiter diary logs if they exist
        st.markdown("##### 🖋️ Recruiter Assessment Log Notes:")
        existing_notes = chosen_candidate.get("Recruiter Notes", "No manual comments recorded yet for this profile candidate.")
        st.warning(existing_notes)
        
    with right_column:
        st.subheader("⚙️ Management Evaluation Panel")
        
        # Wrap our input change selectors inside a sub-form block structure
        with st.form("recruiter_action_form", clear_on_submit=False):
            
            st.markdown("**1. Modify Candidate Core Fields:**")
            # Editable text fields pre-filled with the candidate's existing record details
            new_name = st.text_input("Edit Candidate Name:", value=chosen_candidate.get("Candidate Name", ""))
            new_phone = st.text_input("Edit Contact Phone Line:", value=chosen_candidate.get("Phone", ""))
            new_location = st.text_input("Edit Location Area:", value=chosen_candidate.get("Location", ""))
            new_role = st.text_input("Edit Current Role:", value=chosen_candidate.get("Current Role", ""))
            new_company = st.text_input("Edit Current Company:", value=chosen_candidate.get("Company", ""))
            
            st.markdown("**2. Update Recruitment Review State Status:**")
            # Create interactive button quick triggers by using a selectbox mapped to statuses
            status_list = ["Under Review", "Shortlisted", "Manual Review", "Rejected"]
            
            # Find the default index based on the candidate's current state status string
            default_status_idx = status_list.index(current_state) if current_state in status_list else 0
            
            new_status = st.selectbox(
                "Change Candidate Status Decision:",
                options=status_list,
                index=default_status_idx
            )
            
            st.markdown("**3. Append Recruiter Assessment Notes:**")
            # Text layout area to append text comments
            new_notes_input = st.text_area("Append evaluation notes entry:", placeholder="Add candidate screening feedback or interview remarks here...")
            
            # Submit action button triggers form updates calculations execution
            save_button = st.form_submit_button("Save Changes & Status Logs", use_container_width=True)
            
            if save_button:
                # Compile updated inputs into a dictionary map package
                updated_fields = {
                    "Candidate Name": new_name,
                    "Phone": new_phone,
                    "Location": new_location,
                    "Current Role": new_role,
                    "Company": new_company,
                    "Status": new_status
                }
                
                # Append fresh diary logs onto historical notes rows safely
                if new_notes_input.strip() != "":
                    old_notes_log = chosen_candidate.get("Recruiter Notes", "")
                    if old_notes_log and old_notes_log != "No manual comments recorded yet for this profile candidate.":
                        updated_fields["Recruiter Notes"] = old_notes_log + "\n" + new_notes_input.strip()
                    else:
                        updated_fields["Recruiter Notes"] = new_notes_input.strip()
                
                # Commit updates into our data storage layer using our email primary key lookup tool
                success_flag = update_candidate(candidate_email, updated_fields)
                
                if success_flag:
                    st.success("🎉 Candidate profile records saved successfully! Refreshing dashboard data layout view...")
                    # Force Streamlit to rerender and instantly show updated values on screen
                    st.rerun()
                else:
                    st.error("❌ An issue occurred while attempting to write updates down onto JSON database disk storage.")
