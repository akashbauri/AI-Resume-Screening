import streamlit as st
import pandas as pd
from datetime import datetime
from services.database import load_candidates, update_candidate

# ==========================================
# 1. PAGE CONFIGURATION (CRITICAL ISSUE 1 FIX)
# ==========================================
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
    # ==========================================
    # 2. GLOBAL ANALYTICS METRICS (MISSING FEATURE 1)
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
    
    # Calculate average score safely
    scores = [int(c.get("Match Score", 0)) for c in all_candidates if str(c.get("Match Score", "")).isdigit()]
    avg_score = round(sum(scores) / len(scores)) if scores else 0

    # Render overview layout cards
    col_a, col_b, col_c, col_d, col_e, col_f = st.columns(6)
    col_a.metric("Total Applicants", total_candidates)
    col_b.metric("New Profiles", count_new)
    col_c.metric("Under Review", count_under_review)
    col_d.metric("Interviews Set", count_interview)
    col_e.metric("Hired 🎉", count_hired)
    col_f.metric("Avg Match Fit", f"{avg_score}%")
    
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
        
        # Display meta IDs if available (Missing Feature 4)
        c_id = chosen_candidate.get("Candidate ID", "N/A")
        st.caption(f"**System ID:** {c_id} | **Last Database Sync:** {datetime.now().strftime('%Y-%m-%d')}")
        
        # Core Match Metrics & Progress Bar (Missing Feature 2)
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            score_val = int(chosen_candidate.get("Match Score", 0))
            st.metric("AI Match Fit Score", f"{score_val}%")
            st.progress(score_val / 100)
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
            # CRITICAL ISSUE 2 FIX: Company -> Current Company
            st.write(f"**💼 Employment:** {chosen_candidate.get('Current Role', 'N/A')} at *{chosen_candidate.get('Current Company', 'N/A')}*")
            
            st.markdown("##### 🛠️ Parsed Background Repositories (Missing Feature 4)")
            st.write(f"**💻 Technical Skills:** {chosen_candidate.get('Technical Skills', 'N/A')}")
            st.write(f"**🧠 Soft Skills:** {chosen_candidate.get('Soft Skills', 'N/A')}")
            st.write(f"**🌐 Languages:** {chosen_candidate.get('Languages', 'N/A')}")
            st.write(f"**📜 Certifications:** {chosen_candidate.get('Certifications', 'N/A')}")
            if chosen_candidate.get("LinkedIn"):
                st.write(f"**🔗 Professional Portfolio:** [{chosen_candidate.get('LinkedIn')}]({chosen_candidate.get('LinkedIn')})")

        with tab2:
            # CRITICAL ISSUE 3 FIX: Summary -> AI Summary
            st.markdown("##### 📝 Machine Generation Summary")
            st.info(chosen_candidate.get("AI Summary", "No automated summary evaluation notes recorded for this applicant profile."))
            
            # Skills Matrix Comparison UI (Missing Feature 3)
            st.markdown("##### 🎯 Targeted Requirement Gap Breakdown")
            st.success(f"**✅ Matching Skills Matrix:** {chosen_candidate.get('Matching Skills', 'None explicitly flagged.')}")
            st.error(f"**❌ Identified Missing Skills:** {chosen_candidate.get('Missing Skills', 'None explicitly flagged.')}")
            st.warning(f"**⚠️ Potential Red Flags / Concerns:** {chosen_candidate.get('Potential Concerns', 'No critical standard concerns flagged.')}")

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
            # CRITICAL ISSUE 5 FIX: Company -> Current Company references
            new_company = st.text_input("Edit Current Company:", value=chosen_candidate.get("Current Company", ""))
            
            st.markdown("**2. Update Recruitment Review State Status:**")
            # CRITICAL ISSUE 4 FIX: Synchronized Project Workflow States List
            status_list = ["New", "Under Review", "Interview Scheduled", "Hired", "Rejected"]
            current_state = chosen_candidate.get("Status", "New")
            default_status_idx = status_list.index(current_state) if current_state in status_list else 0
            
            new_status = st.selectbox(
                "Change Candidate Status Decision:",
                options=status_list,
                index=default_status_idx
            )
            
            # Missing Feature 5: Option to override recommendations conditionally if necessary
            new_recommendation = st.text_input("Override AI Recommendation (Optional):", value=chosen_candidate.get("Recommendation", "N/A"))
            
            st.markdown("**3. Append Recruiter Assessment Notes:**")
            new_notes_input = st.text_area("Append evaluation notes entry:", placeholder="Add candidate screening feedback, vetting logs, or interview remarks here...")
            
            # Submit Actions execution
            save_button = st.form_submit_button("Save Changes & Status Logs", use_container_width=True)
            
            if save_button:
                # Compile matching dictionary package map structure
                updated_fields = {
                    "Candidate Name": new_name,
                    "Phone": new_phone,
                    "Location": new_location,
                    "Current Role": new_role,
                    "Current Company": new_company, # Structural alignment change verified
                    "Status": new_status,
                    "Recommendation": new_recommendation
                }
                
                # Append notes strings safely onto historical logs text walls
                if new_notes_input.strip() != "":
                    old_notes_log = chosen_candidate.get("Recruiter Notes", "")
                    if old_notes_log and old_notes_log != "No manual comments recorded yet for this profile candidate.":
                        updated_fields["Recruiter Notes"] = old_notes_log + "\n" + f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] " + new_notes_input.strip()
                    else:
                        updated_fields["Recruiter Notes"] = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] " + new_notes_input.strip()
                
                # Commit payload down into our data engine layer primary key lookup wrapper
                success_flag = update_candidate(candidate_email, updated_fields)
                
                if success_flag:
                    st.success("🎉 Candidate profile records saved successfully! Refreshing view...")
                    st.rerun()
                else:
                    st.error("❌ An issue occurred while attempting to write updates down onto the JSON storage engine layer.")
