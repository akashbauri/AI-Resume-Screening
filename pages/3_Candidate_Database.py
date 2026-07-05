# Import our web design components, tables tool, and the updated database service
import streamlit as st
import pandas as pd
from services.database import load_candidates

# Set page layout to wide for a highly scannable, professional grid experience
st.set_page_layout = "wide"

st.title("🗄️ Candidate Database Hub")
st.write("Browse, search, sort, and filter through all analyzed candidate profiles below.")

# Load the master candidate profiles list from our JSON database system
all_candidates = load_candidates()

if not all_candidates:
    st.info("ℹ&nbsp; No candidates found in the database yet. Go upload a resume to populate this hub!")
else:
    # --- SEARCH & FILTER CONTROLS ---
    st.subheader("🔍 Filters & Search Controls")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_query = st.text_input("Search candidates by name, email, or key skills:", placeholder="e.g., Jane Doe, Python, AWS...")
    with col2:
        # Collect unique recommendations available in our dataset to build filter items
        rec_options = ["All"] + sorted(list(set([str(c.get("Recommendation", "")) for c in all_candidates if c.get("Recommendation")])))
        filter_rec = st.selectbox("Filter by AI Recommendation:", rec_options)
    with col3:
        # Collect unique statuses available to build filter items
        status_options = ["All"] + sorted(list(set([str(c.get("Status", "")) for c in all_candidates if c.get("Status")])))
        filter_status = st.selectbox("Filter by Processing Status:", status_options)

    # Apply search and filter logic directly across our live data array list
    filtered_candidates = []
    for c in all_candidates:
        name = str(c.get("Candidate Name", "")).lower()
        email = str(c.get("Email", "")).lower()
        tech_skills = " ".join([str(s) for s in c.get("Technical Skills", [])]).lower()
        soft_skills = " ".join([str(s) for s in c.get("Soft Skills", [])]).lower()
        
        # Check text search matches
        match_query = (search_query.lower() in name or 
                       search_query.lower() in email or 
                       search_query.lower() in tech_skills or 
                       search_query.lower() in soft_skills)
                       
        # Check dropdown filter selector choices
        match_rec = (filter_rec == "All" or str(c.get("Recommendation", "")) == filter_rec)
        match_status = (filter_status == "All" or str(c.get("Status", "")) == filter_status)
        
        if match_query and match_rec and match_status:
            filtered_candidates.append(c)

    # --- SORTING CONTROLS ---
    sort_col1, sort_col2 = st.columns([1, 3])
    with sort_col1:
        sort_by = st.selectbox("Sort data by:", ["Match Score (High to Low)", "Name (A-Z)", "Newest Additions"])
        
    if sort_by == "Match Score (High to Low)":
        filtered_candidates = sorted(filtered_candidates, key=lambda x: int(x.get("Match Score", 0)), reverse=True)
    elif sort_by == "Name (A-Z)":
        filtered_candidates = sorted(filtered_candidates, key=lambda x: str(x.get("Candidate Name", "")).lower())
    elif sort_by == "Newest Additions":
        filtered_candidates = sorted(filtered_candidates, key=lambda x: str(x.get("Created Time", "")), reverse=True)

    st.markdown("---")

    # --- GRID DASHBOARD METRICS SUMMARY ---
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Filtered Total Results", len(filtered_candidates))
    with m2:
        high_score = max([int(c.get("Match Score", 0)) for c in filtered_candidates]) if filtered_candidates else 0
        st.metric("Top Fit Score in View", f"{high_score}%")
    with m3:
        st.metric("Total Master Pool Size", len(all_candidates))

    st.markdown("### 📋 Applicant Records Grid Table")

    # Build an interactive data overview frame using structural columns matching requirements
    header_cols = st.columns([2, 2, 3, 1, 2, 2])
    with header_cols[0]: st.markdown("**Name**")
    with header_cols[1]: st.markdown("**Email**")
    with header_cols[2]: st.markdown("**Current Role / Experience**")
    with header_cols[3]: st.markdown("**Score**")
    with header_cols[4]: st.markdown("**Recommendation**")
    with header_cols[5]: st.markdown("**Status**")

    # Display candidate block information row-by-row
    for candidate in filtered_candidates:
        row_cols = st.columns([2, 2, 3, 1, 2, 2])
        
        # Render clean fallback parameters if value properties are blank
        cand_name = candidate.get("Candidate Name", "Unknown")
        cand_email = candidate.get("Email", "N/A")
        cand_role = candidate.get("Current Role", "N/A")
        cand_company = candidate.get("Company", "")
        role_summary = f"{cand_role} at {cand_company}" if cand_company else cand_role
        cand_score = f"{candidate.get('Match Score', 0)}%"
        cand_rec = candidate.get("Recommendation", "N/A")
        cand_status = candidate.get("Status", "Under Review")
        
        with row_cols[0]: st.write(cand_name)
        with row_cols[1]: st.write(cand_email)
        with row_cols[2]: st.write(role_summary)
        with row_cols[3]: st.write(cand_score)
        with row_cols[4]: st.write(cand_rec)
        with row_cols[5]: st.write(cand_status)

        # --- EXPANDABLE CARD FOR ALL DETAILS ---
        # Using expandable cards allows a recruiter to explore complex data points cleanly on click
        with st.expander(f"🔍 View Full Comprehensive Profile Summary Analysis for {cand_name}"):
            tab_summary, tab_details, tab_skills = st.tabs(["📊 Matching Summary", "🎓 Profile Background & History", "🛠️ Extracted Competency Skills"])
            
            with tab_summary:
                st.markdown(f"#### AI Summary Evaluation")
                st.info(candidate.get("Summary", "No automated matching evaluation notes recorded for this applicant profile."))
                
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
                        
            with tab_details:
                st.markdown(f"**📍 Current Location Area:** {candidate.get('Location', 'N/A')}")
                st.markdown(f"**📂 Tracked Resume Target File Reference:** `{candidate.get('Resume File', 'N/A')}`")
                st.markdown(f"**⏰ Data Entry Creation Timestamp:** `{candidate.get('Created Time', 'N/A')}`")
                
                st.markdown("##### Professional Experience Timeline")
                exp_records = candidate.get("Experience", [])
                if isinstance(exp_records, list) and exp_records:
                    for item in exp_records:
                        st.markdown(f"- **{item.get('Job Title', 'N/A')}** at *{item.get('Company', 'N/A')}* ({item.get('Duration', 'N/A')})")
                        st.caption(item.get("Responsibilities", ""))
                else:
                    st.write(str(exp_records) if exp_records else "No work experience history details parsed available.")
                    
                st.markdown("##### Academic Education Profile Background")
                edu_records = candidate.get("Education", [])
                if isinstance(edu_records, list) and edu_records:
                    for item in edu_records:
                        st.markdown(f"- **{item.get('Degree', 'N/A')}** — *{item.get('School/University', 'N/A')}* ({item.get('Year', 'N/A')})")
                else:
                    st.write(str(edu_records) if edu_records else "No education listings records parsed available.")
                    
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
