# Import our web design components and the updated database service functions
import streamlit as st
from services.database import load_candidates, delete_candidate

# Set page configuration layout to wide for a highly scannable grid experience
# This MUST be the first Streamlit command executed in the script file.
st.set_page_config(
    page_title="Candidate Database Hub",
    page_icon="🗄️",
    layout="wide"
)

st.title("🗄️ Candidate Database Hub")
st.write("Browse, search, sort, and filter through all analyzed candidate profiles below.")

# Load the master candidate profiles list from our JSON database system
all_candidates = load_candidates()

if not all_candidates:
    st.info("ℹ️ No candidates found in the database yet. Go upload a resume to populate this hub!")
else:
    # --- SEARCH & FILTER CONTROLS ---
    st.subheader("🔍 Filters & Search Controls")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_query = st.text_input("Search candidates by name, email, role, company, or skills:", placeholder="e.g., Jane Doe, Python, AWS...")
    with col2:
        # Collect unique recommendations available in our dataset to build filter items
        rec_options = ["All"] + sorted(list(set([str(c.get("Recommendation", "")) for c in all_candidates if c.get("Recommendation")])))
        filter_rec = st.selectbox("Filter by AI Recommendation:", rec_options)
    with col3:
        # Collect unique statuses available to build filter items
        status_options = ["All"] + sorted(list(set([str(c.get("Status", "")) for c in all_candidates if c.get("Status")])))
        filter_status = st.selectbox("Filter by Processing Status:", status_options)

    # Process search query string once outside the processing loop
    query = search_query.strip().lower()

    # Apply search and filter logic directly across our live data array list
    filtered_candidates = []
    for c in all_candidates:
        name = str(c.get("Candidate Name", "")).lower()
        email = str(c.get("Email", "")).lower()
        current_role = str(c.get("Current Role", "")).lower()
        current_company = str(c.get("Current Company", "")).lower()
        recommendation = str(c.get("Recommendation", "")).lower()
        
        tech_skills = " ".join([str(s) for s in c.get("Technical Skills", [])]).lower()
        soft_skills = " ".join([str(s) for s in c.get("Soft Skills", [])]).lower()
        
        # Check text search matches (optimized performance)
        match_query = (not query or
                       query in name or 
                       query in email or 
                       query in current_role or
                       query in current_company or
                       query in recommendation or
                       query in tech_skills or 
                       query in soft_skills)
                       
        # Check dropdown filter selector choices
        match_rec = (filter_rec == "All" or str(c.get("Recommendation", "")) == filter_rec)
        match_status = (filter_status == "All" or str(c.get("Status", "")) == filter_status)
        
        if match_query and match_rec and match_status:
            filtered_candidates.append(c)

    # Helper to parse scores safely handling percentage marks and string float variants
    def get_safe_score(candidate_obj):
        raw_score = str(candidate_obj.get("Match Score", "0")).replace("%", "").strip()
        try:
            return int(float(raw_score))
        except Exception:
            return 0

    # --- SORTING CONTROLS ---
    sort_col1, sort_col2 = st.columns([1, 3])
    with sort_col1:
        sort_by = st.selectbox("Sort data by:", ["Match Score (High to Low)", "Name (A-Z)", "Newest Additions"])
        
    if sort_by == "Match Score (High to Low)":
        filtered_candidates = sorted(filtered_candidates, key=get_safe_score, reverse=True)
    elif sort_by == "Name (A-Z)":
        filtered_candidates = sorted(filtered_candidates, key=lambda x: str(x.get("Candidate Name", "")).lower())
    elif sort_by == "Newest Additions":
        # Lexical chronological sorting works perfectly since our layout uses the "YYYY-MM-DD HH:MM:SS" format
        filtered_candidates = sorted(filtered_candidates, key=lambda x: str(x.get("Created Time", "")), reverse=True)

    st.markdown("---")

    # --- GRID DASHBOARD METRICS SUMMARY ---
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Filtered Total Results", len(filtered_candidates))
    with m2:
        high_score = max([get_safe_score(c) for c in filtered_candidates]) if filtered_candidates else 0
        st.metric("Top Fit Score in View", f"{high_score}%")
    with m3:
        st.metric("Total Master Pool Size", len(all_candidates))

    st.markdown("### 📋 Applicant Records Grid Table")

    # Build an interactive data overview frame using structural columns matching requirements
    header_cols = st.columns([2, 2, 3, 1, 2, 1.5, 1])
    with header_cols[0]: st.markdown("**Name**")
    with header_cols[1]: st.markdown("**Email**")
    with header_cols[2]: st.markdown("**Current Role / Company**")
    with header_cols[3]: st.markdown("**Score**")
    with header_cols[4]: st.markdown("**Recommendation**")
    with header_cols[5]: st.markdown("**Status**")
    with header_cols[6]: st.markdown("**Actions**")

    # Display candidate block information row-by-row
    for candidate in filtered_candidates:
        row_cols = st.columns([2, 2, 3, 1, 2, 1.5, 1])
        
        cand_name = candidate.get("Candidate Name", "Unknown")
        cand_email = candidate.get("Email", "N/A")
        cand_role = candidate.get("Current Role", "N/A")
        cand_company = candidate.get("Current Company", "")
        role_summary = f"{cand_role} at {cand_company}" if cand_company else cand_role
        
        score_val = get_safe_score(candidate)
        cand_score = f"{score_val}%"
        cand_rec = candidate.get("Recommendation", "N/A")
        cand_status = candidate.get("Status", "New")
        
        # Format visual badge markers for Recommendations
        if cand_rec == "Shortlisted":
            rec_badge = "🟢 Shortlisted"
        elif cand_rec == "Manual Review":
            rec_badge = "🟡 Manual Review"
        else:
            rec_badge = "🔴 Rejected"

        # Format visual status indicators to enrich scannability
        if cand_status == "New":
            status_badge = "🟢 New"
        elif cand_status == "Under Review":
            status_badge = "🟡 Under Review"
        elif cand_status == "Interview Scheduled":
            status_badge = "🔵 Interview Scheduled"
        elif cand_status == "Hired":
            status_badge = "⚫ Hired"
        elif cand_status == "Rejected":
            status_badge = "🔴 Rejected"
        else:
            status_badge = f"⚪ {cand_status}"

        with row_cols[0]: st.write(cand_name)
        with row_cols[1]: st.write(cand_email)
        with row_cols[2]: st.write(role_summary)
        with row_cols[3]: st.write(cand_score)
        with row_cols[4]: st.write(rec_badge)
        with row_cols[5]: st.write(status_badge)
        
        # Add interactive removal controls hook with defensive confirmation workflows
        with row_cols[6]:
            if st.button("🗑️", key=f"del_init_{cand_email}"):
                st.session_state[f"confirm_delete_{cand_email}"] = True
                
            if st.session_state.get(f"confirm_delete_{cand_email}", False):
                st.warning("Confirm?")
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("✅ Yes", key=f"del_yes_{cand_email}"):
                        if delete_candidate(cand_email):
                            st.success("Removed!")
                            del st.session_state[f"confirm_delete_{cand_email}"]
                            st.rerun()
                        else:
                            st.error("Error occurred")
                with c_btn2:
                    if st.button("❌ No", key=f"del_no_{cand_email}"):
                        del st.session_state[f"confirm_delete_{cand_email}"]
                        st.rerun()

        # --- EXPANDABLE CARD FOR ALL DETAILS ---
        with st.expander(f"🔍 View Full Comprehensive Profile Summary Analysis for {cand_name}"):
            tab_summary, tab_details, tab_skills = st.tabs(["📊 Matching Summary", "🎓 Profile Background & History", "🛠️ Extracted Competency Skills"])
            
            with tab_summary:
                st.markdown("#### AI Summary Evaluation")
                st.info(candidate.get("AI Summary", "No automated matching evaluation notes recorded for this applicant profile."))
                
                # Render visual performance bar indicators for direct review scaling properties
                st.markdown(f"**Match Progress Vector Fit:** {score_val}%")
                st.progress(score_val / 100.0)
                
                # Setup side-by-side matching skill details list breakdowns
                sc1, sc2 = st.columns(2)
                with sc1:
                    st.markdown("**🟢 Identified Overlapping Match Skills:**")
                    matching_skills_list = candidate.get("Matching Skills", [])
                    if matching_skills_list:
                        st.write(", ".join(matching_skills_list))
                    else:
                        st.caption("No matching skills found.")
                with sc2:
                    st.markdown("**🔴 Missing Role Priority Requirements:**")
                    missing_skills_list = candidate.get("Missing Skills", [])
                    if missing_skills_list:
                        st.write(", ".join(missing_skills_list))
                    else:
                        st.caption("No missing skills identified.")
                        
                # Display potential structural alert flags if present in data blocks
                concerns_list = candidate.get("Potential Concerns", [])
                if concerns_list:
                    st.markdown("**⚠️ Potential Concerns / Flags:**")
                    for concern in concerns_list:
                        st.markdown(f"- {concern}")
                        
            with tab_details:
                # Show unique tracking hashes / Candidate IDs if recorded in database
                if candidate.get("Candidate ID"):
                    st.markdown(f"**🆔 Candidate Unique Record identifier:** `{candidate.get('Candidate ID')}`")
                st.markdown(f"**📍 Current Location Area:** {candidate.get('Location', 'N/A')}")
                st.markdown(f"**⏰ Data Entry Creation Timestamp:** `{candidate.get('Created Time', 'N/A')}`")
                st.markdown(f"**🔄 Last System Synchronization Marker:** `{candidate.get('Updated Time', 'N/A')}`")
                if candidate.get("LinkedIn"):
                    st.markdown(f"**🔗 Professional Network Link:** [{candidate.get('LinkedIn')}]({candidate.get('LinkedIn')})")
                
                st.markdown("##### Professional Experience Timeline")
                exp_records = candidate.get("Experience", [])
                if isinstance(exp_records, list) and exp_records:
                    for item in exp_records:
                        st.markdown(f"- **{item.get('Job Title', 'N/A')}** at *{item.get('Company', 'N/A')}* ({item.get('Duration', 'N/A')})")
                        st.caption(item.get("Description", "No detailed responsibilities text provided."))
                else:
                    st.write("No work experience history details parsed available.")
                    
                st.markdown("##### Academic Education Profile Background")
                edu_records = candidate.get("Education", [])
                if isinstance(edu_records, list) and edu_records:
                    for item in edu_records:
                        st.markdown(f"- **{item.get('Degree', 'N/A')}** — *{item.get('School/University', 'N/A')}* ({item.get('Year', 'N/A')})")
                else:
                    st.write("No education listings records parsed available.")
                    
            with tab_skills:
                st.markdown("**🛠️ Technical Engineering Core Competencies:**")
                st.write(", ".join(candidate.get("Technical Skills", [])) if candidate.get("Technical Skills") else "N/A")
                
                st.markdown("**🤝 Interpersonal / Soft Professional Talents:**")
                st.write(", ".join(candidate.get("Soft Skills", [])) if candidate.get("Soft Skills") else "N/A")
                
                st.markdown("**🗣️ Communicated Profile Languages:**")
                st.write(", ".join(candidate.get("Languages", [])) if candidate.get("Languages") else "N/A")
                
                st.markdown("**🏆 Professional Certifications held:**")
                st.write(", ".join(candidate.get("Certifications", [])) if candidate.get("Certifications") else "N/A")
                
        st.markdown("---")
