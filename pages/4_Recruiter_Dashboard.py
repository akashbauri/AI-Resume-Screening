# Import our web interface components and the updated database service functions
import streamlit as st
from datetime import datetime
from services.database import load_candidates, update_candidate

# Set page configuration layout to wide for a clear side-by-side split action board
# This MUST be the first Streamlit command executed in the script file.
st.set_page_config(
    page_title="Recruiter Action & Review Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Recruiter Action & Review Dashboard")
st.write("Analyze pool-wide metrics, perform manual verification assessments, and update candidate records.")

# Fetch master records from the database layer
all_candidates = load_candidates()

# Check if there are no candidates to manage yet
if not all_candidates:
    st.info("ℹ️ The dashboard is empty because no candidates exist in the database yet. Please go upload a resume file first!")
else:
    # Helper to parse scores safely handling percentage marks and string float variants
    def get_safe_score(candidate_obj):
        raw_score = str(candidate_obj.get("Match Score", "0")).replace("%", "").strip()
        try:
            return int(float(raw_score))
        except Exception:
            return 0

    # Helper to format lists or strings into clean, professional comma-separated text
    def format_list_field(field_value):
        if not field_value:
            return "N/A"
        if isinstance(field_value, list):
            return ", ".join(str(item) for item in field_value)
        return str(field_value)

    # ==========================================
    # 2. GLOBAL ANALYTICS METRICS
    # ==========================================
    st.markdown("### 📈 Talent Pool Overview")
    
    total_candidates = len(all_candidates)
    
    # Calculate statuses safely
    statuses = [c.get("Status", "New") for c in all_candidates]
    count_new = statuses.count("New")
    count_under_review = statuses.count("Under Review")
    count_interview = statuses.count("Interview Scheduled")
    count_hired = statuses.count("Hired")
    count_rejected = statuses.count("Rejected")
    
    # Calculate average score safely using the safe score parser
    scores = [get_safe_score(c) for c in all_candidates]
    avg_score = round(sum(scores) / len(scores)) if scores else 0

    # Render overview layout cards including the requested Rejected metric card
    col_a, col_b, col_c, col_d, col_e, col_f, col_g = st.columns(7)
    col_a.metric("Total Applicants", total_candidates)
    col_b.metric("New Profiles", count_new)
    col_c.metric("Under Review", count_under_review)
    col_d.metric("Interviews Set", count_interview)
    col_e.metric("Hired 🎉", count_hired)
    col_f.metric("Rejected 🔴", count_rejected)
    col_g.metric("Avg Match Fit", f"{avg_score}%")
    
    st.markdown("---")

    # ==========================================
    # 3. CANDIDATE SELECTION
    # ==========================================
    # Unique string identifier lookup map
    candidate_map = {
        f"{c.get('Candidate Name', 'Unknown')} ({c.get('Email', 'N/A')})": c 
        for c in all_candidates
    }
    
    selected_key = st.selectbox("🎯 Choose a candidate profile to manage:", list(candidate_map.keys()))
    chosen_candidate = candidate_map[selected_key]
    candidate_email = chosen_candidate.get("Email", "")
    
    st.markdown("---")
    
    # ==========================================
    # 4. SIDE-BY-SIDE WORKING LAYOUT
    # ==========================================
    left_column, right_column = st.columns([3, 2])
    
    # --- LEFT COLUMN: DATA VISUALIZATION & PROFILE INSIGHTS ---
    with left_column:
        st.subheader(f"📄 Profile: {chosen_candidate.get('Candidate Name', 'Unknown')}")
        
        # Display meta IDs along with structural creation and updated timestamps
        c_id = chosen_candidate.get("Candidate ID", "N/A")
        created_time = chosen_candidate.get("Created Time", "N/A")
        updated_time = chosen_candidate.get("Updated Time", "N/A")
        st.caption(f"**System ID:** {c_id} | **Created:** {created_time} | **Last System Sync:** {updated_time}")
        
        # Core Match Metrics & Progress Bar using the safe score parser
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            score_val = get_safe_score(chosen_candidate)
            st.metric("AI Match Fit Score", f"{score_val}%")
            st.progress(score_val / 100.0)
        with m_col2:
            current_rec = chosen_candidate.get("Recommendation", "N/A")
            st.metric("AI Pipeline Recommendation", current_rec)
            
        st.markdown("### 🗂️ Detailed Breakdown")
        
        # Tabs for clean scannable navigation across dense parsed data
        tab1, tab2, tab3 = st.tabs(["Core Details & Skills", "AI Matching Analysis", "Internal Assessment Logs"])
        
        with tab1:
            st.markdown("##### 📞 Contact & Demographics")
            st.write(f"**📧 Email Address:** {candidate_email}")
            st.write(f"**📞 Contact Number:** {chosen_candidate.get('Phone', 'N/A')}")
            st.write(f"**📍 Current Location:** {chosen_candidate.get('Location', 'N/A')}")
            st.write(f"**💼 Employment:** {chosen_candidate.get('Current Role', 'N/A')} at *{chosen_candidate.get('Current Company', 'N/A')}*")
            st.write(f"**🧑‍💼 Total Experience:** {chosen_candidate.get('Total Experience', '0 Months')}")
            
            st.markdown("##### 🛠️ Parsed Background Repositories")
            st.write(f"**💻 Technical Skills:** {format_list_field(chosen_candidate.get('Technical Skills'))}")
            st.write(f"**🧠 Soft Skills:** {format_list_field(chosen_candidate.get('Soft Skills'))}")
            st.write(f"**🌐 Languages:** {format_list_field(chosen_candidate.get('Languages'))}")
            st.write(f"**📜 Certifications:** {format_list_field(chosen_candidate.get('Certifications'))}")
            if chosen_candidate.get("LinkedIn"):
                st.write(f"**🔗 Professional Network Link:** [{chosen_candidate.get('LinkedIn')}]({chosen_candidate.get('LinkedIn')})")

        with tab2:
            st.markdown("##### 📝 Machine Generation Summary")
            st.info(chosen_candidate.get("AI Summary", "No automated summary evaluation notes recorded for this applicant profile."))
            
            # Skills Matrix Comparison UI
            st.markdown("##### 🎯 Targeted Requirement Gap Breakdown")
            st.success(f"**✅ Matching Skills Matrix:** {format_list_field(chosen_candidate.get('Matching Skills'))}")
            st.error(f"**❌ Identified Missing Skills:** {format_list_field(chosen_candidate.get('Missing Skills'))}")
            st.warning(f"**⚠️ Potential Red Flags / Concerns:** {format_list_field(chosen_candidate.get('Potential Concerns'))}")

        with tab3:
            st.markdown("##### 🖋️ Historical Recruiter Diary Logs:")
            existing_notes = chosen_candidate.get("Recruiter Notes", "No manual comments recorded yet for this profile candidate.")
            st.warning(existing_notes)

    # --- RIGHT COLUMN: ACTIVE MANAGEMENT/MODIFICATION FORM ---
    with right_column:
        st.subheader("⚙️ Management Evaluation Panel")
        
        with st.form("recruiter_action_form", clear_on_submit=False):
            st.markdown("**1. Modify Candidate Core Fields:**")
            new_name = st.text_input("Edit Candidate Name:", value=chosen_candidate.get("Candidate Name", ""))
            new_phone = st.text_input("Edit Contact Phone Line:", value=chosen_candidate.get("Phone", ""))
            new_location = st.text_input("Edit Location Area:", value=chosen_candidate.get("Location", ""))
            new_role = st.text_input("Edit Current Role:", value=chosen_candidate.get("Current Role", ""))
            new_company = st.text_input("Edit Current Company:", value=chosen_candidate.get("Current Company", ""))
            st.write(f"**🧑‍💼 Total Experience:** {chosen_candidate.get('Total Experience', '0 Months')}")
            
            st.markdown("**2. Update Recruitment Review State Status:**")
            # Synchronized Project Workflow States List
            status_list = ["New", "Under Review", "Interview Scheduled", "Hired", "Rejected"]
            current_state = chosen_candidate.get("Status", "New")
            default_status_idx = status_list.index(current_state) if current_state in status_list else 0
            
            new_status = st.selectbox(
                "Change Candidate Status Decision:",
                options=status_list,
                index=default_status_idx
            )
            
            # Structured Recommendation options dropdown instead of a free-text layout field
            rec_list = ["Shortlisted", "Manual Review", "Rejected"]
            default_rec_idx = rec_list.index(current_rec) if current_rec in rec_list else 1
            
            new_recommendation = st.selectbox(
                "Modify Operational Recommendation:",
                options=rec_list,
                index=default_rec_idx
            )
            
            st.markdown("**3. Append Recruiter Assessment Notes:**")
            new_notes_input = st.text_area("Append evaluation notes entry:", placeholder="Add candidate screening feedback, vetting logs, or interview remarks here...")
            
            # Submit Actions execution using correct boolean state assignment mapping pattern
            save_button = st.form_submit_button("Save Changes & Status Logs", use_container_width=True)
            
            if save_button:
                # Compile matching dictionary package map structure with an automated sync timestamp override
                updated_fields = {
                    "Candidate Name": new_name,
                    "Phone": new_phone,
                    "Location": new_location,
                    "Current Role": new_role,
                    "Current Company": new_company,
                    "Status": new_status,
                    "Recommendation": new_recommendation,
                    "Updated Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Append notes strings safely onto historical logs text walls
                if new_notes_input.strip() != "":
                    old_notes_log = chosen_candidate.get("Recruiter Notes", "")
                    timestamp_str = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}]"
                    if old_notes_log and old_notes_log != "No manual comments recorded yet for this profile candidate.":
                        updated_fields["Recruiter Notes"] = f"{old_notes_log}\n{timestamp_str} {new_notes_input.strip()}"
                    else:
                        updated_fields["Recruiter Notes"] = f"{timestamp_str} {new_notes_input.strip()}"
                
                # Commit payload down into our data engine layer primary key lookup wrapper
                success_flag = update_candidate(candidate_email, updated_fields)
                
                if success_flag:
                    st.success("🎉 Candidate profile records saved successfully! Refreshing view...")
                    st.rerun()
                else:
                    st.error("❌ An issue occurred while attempting to write updates down onto the JSON storage engine layer.")
