# Import the tools we need to build our app, handle local file storage, tracking, and identifiers
import streamlit as st
import os
import uuid
from datetime import datetime

# Import our custom backend worker tools matching your architectural separation
from services.resume_parser import extract_resume_text
from services.llm_service import parse_resume as parse_resume_with_ai
from services.matcher import run_resume_match as match_candidate
from services.database import save_candidate, load_candidates
from services.logger import log_event

# Define the maximum file size allowed: 10 Megabytes
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
UPLOAD_FOLDER = "uploads"

# --- SESSION STATE INITIALIZATION ---
# Using structured state avoids flashing, double execution, or losing data during state changes
if "pipeline_results" not in st.session_state:
    st.session_state.pipeline_results = None

# --- HELPERS FOR STABLE SCHEMAS & NORMALIZATION ---
def generate_candidate_id():
    """Generates a synchronized rolling candidate ID: CAND-000001 based on rows length."""
    try:
        existing = load_candidates()
        next_num = len(existing) + 1
        return f"CAND-{next_num:06d}"
    except Exception:
        return f"CAND-{uuid.uuid4().hex[:6].upper()}"

def normalize_to_list(data_field):
    """Guarantees nested entities remain an iterable list even if the LLM drops flat data strings."""
    if isinstance(data_field, list):
        return data_field
    if isinstance(data_field, str) and data_field.strip():
        return [data_field.strip()]
    return []

# --- START OF THE PAGE LAYOUT ---

st.title("🤖 AI Resume Screening")
st.write("Upload a candidate resume, paste the job description, and let AI evaluate the candidate.")

st.markdown("---")

# --- SECTION 1: UPLOAD RESUME ---
st.subheader("📄 Upload Resume")
uploaded_file = st.file_uploader(
    label="Upload candidate resume file (PDF, DOCX, or TXT formats supported)",
    type=["pdf", "docx", "txt"]
)

if uploaded_file is not None:
    if uploaded_file.size > MAX_FILE_SIZE_BYTES:
        st.error(f"❌ This file exceeds the 10MB limit! Your file size: {uploaded_file.size / (1024*1024):.2f}MB.")
        uploaded_file = None
    else:
        file_size_kb = uploaded_file.size / 1024
        st.write(f"**File Name:** `{uploaded_file.name}`")
        st.write(f"**File Size:** `{file_size_kb:.2f} KB`")
        st.write(f"**File Type:** `{uploaded_file.type}`")

st.markdown("---")

# --- SECTION 2: JOB DESCRIPTION ---
st.subheader("📋 Job Description")
job_description_input = st.text_area(
    label="Provide the corporate requirements target details below:",
    placeholder="Paste the complete Job Description here...",
    height=320
)

st.markdown("---")

# --- SECTION 3: ANALYZE CANDIDATE TRIGGER BUTTON ---
input_validation_ready = (uploaded_file is not None and len(job_description_input.strip()) > 0)
analyze_button = st.button(
    label="🚀 Analyze Candidate",
    disabled=not input_validation_ready,
    use_container_width=True
)

# --- BACKEND PIPELINE EXECUTION ---
if analyze_button:
    st.session_state.pipeline_results = None
    log_event(category="UPLOAD", message=f"Triggering automated screening pipeline for: {uploaded_file.name}")
    
    # Use standard loading wrapper components
    with st.spinner("Processing applicant profile through the automated execution stream..."):
        temp_path = None
        try:
            # Setup indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # --- PRE-STEP: BUFFER WRITING ---
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            temp_path = os.path.join(UPLOAD_FOLDER, f"temp_{uuid.uuid4().hex}_{uploaded_file.name}")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # --- STEP 1: EXTRACT RESUME TEXT ---
            status_text.text("🔄 Extracting Resume...")
            progress_bar.progress(10)
            
            if uploaded_file.name.lower().endswith(".txt"):
                with open(temp_path, "r", encoding="utf-8") as txt_f:
                    extracted_plain_text = txt_f.read()
            else:
                extracted_plain_text = extract_resume_text(temp_path)
            
            # --- STEP 2: PARSE RESUME ---
            status_text.text("🧠 Running AI Resume Parsing...")
            progress_bar.progress(35)
            parsed_json_profile = parse_resume_with_ai(extracted_plain_text)
            
            if not parsed_json_profile or "error" in parsed_json_profile:
                raise RuntimeError(parsed_json_profile.get("error", "The parsing stage returned empty profiles."))
                
            # --- STEP 3: COMPARE RESUME ---
            status_text.text("⚡ Matching Resume with Job Description...")
            progress_bar.progress(70)
            match_results = match_candidate(parsed_json_profile, job_description_input)
            
            if not match_results or "error" in match_results:
                raise RuntimeError(match_results.get("error", "The matching engine failed to process outputs."))
                
            # --- STEP 4: AUTOMATIC STATUS DETERMINATION & DATABASE STORAGE ---
            status_text.text("💾 Saving Candidate...")
            progress_bar.progress(100)
            
            # Safe parser implementation for Match Score handling percentage marks and string floats
            try:
                score_val = int(float(str(match_results.get("Match Score", 0)).replace("%", "").strip()))
            except Exception:
                score_val = 0
            
            # Determine mapping constraints automatically using condition expressions
            if score_val >= 80:
                auto_status = "Shortlisted"
                clean_rec = "Shortlisted"
            elif score_val >= 50:
                auto_status = "Manual Review"
                clean_rec = "Manual Review"
            else:
                auto_status = "Rejected"
                clean_rec = "Rejected"

            timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            candidate_uid = generate_candidate_id()
            
            # Assemble our standard integrated candidate schema record map
            consolidated_candidate_record = {
                "Candidate ID": candidate_uid,
                "Candidate Name": parsed_json_profile.get("Candidate Name", "Unknown Applicant"),
                "Email": parsed_json_profile.get("Email", "N/A"),
                "Phone": parsed_json_profile.get("Phone", "N/A"),
                "Location": parsed_json_profile.get("Location", "N/A"),
                "Current Role": parsed_json_profile.get("Current Role", "N/A"),
                "Current Company": parsed_json_profile.get("Current Company", "N/A"),
                "Experience": normalize_to_list(parsed_json_profile.get("Experience", [])),
                "Education": normalize_to_list(parsed_json_profile.get("Education", [])),
                "Technical Skills": normalize_to_list(parsed_json_profile.get("Technical Skills", [])),
                "Soft Skills": normalize_to_list(parsed_json_profile.get("Soft Skills", [])),
                "Languages": normalize_to_list(parsed_json_profile.get("Languages", [])),
                "Projects": normalize_to_list(parsed_json_profile.get("Projects", [])),
                "Certifications": normalize_to_list(parsed_json_profile.get("Certifications", [])),
                "Match Score": score_val,
                "Matching Skills": normalize_to_list(match_results.get("Matching Skills", [])),
                "Missing Skills": normalize_to_list(match_results.get("Missing Skills", [])),
                "Relevant Experience": match_results.get("Relevant Experience", "N/A"),
                "Potential Concerns": normalize_to_list(match_results.get("Potential Concerns", [])),
                "AI Summary": match_results.get("AI Summary", ""),
                "Recommendation": clean_rec,
                "Status": auto_status,
                "Application Status": auto_status,
                "Resume File": uploaded_file.name,
                "Job Description": job_description_input,
                "Created Time": timestamp_now,
                "Updated Time": timestamp_now
            }
            
            # Commit the consolidated record entry safely into our JSON database file structure
            save_candidate(consolidated_candidate_record)
            
            status_text.text("Completed")
            st.session_state.pipeline_results = consolidated_candidate_record
            
        except Exception as err:
            st.error(f"❌ An error occurred during processing: {str(err)}")
            log_event(category="ERROR", message=f"Pipeline exception: {str(err)}", level="ERROR")
        finally:
            # Ephemeral system cleanup safeguards: Always scratch out raw binaries to leave zero leakage signatures
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

st.markdown("---")

# --- SECTION 4: AI RESULTS & SCREENING VISUAL CARDS DISPLAY ---
if st.session_state.pipeline_results is not None:
    res = st.session_state.pipeline_results
    
    st.success("✅ Candidate successfully analyzed and committed to the database.")
    
    # Split UI metrics elements professionally
    st.subheader("📊 AI Match Evaluation Metrics")
    col_score, col_rec = st.columns([2, 1])
    
    with col_score:
        st.write(f"**Fit Match Score Compatibility:** `{res['Match Score']}%`")
        st.progress(res["Match Score"] / 100.0)
    with col_rec:
        # Display color indicators dynamically on the UI side
        ui_badge = res["Recommendation"]
        if ui_badge == "Shortlisted":
            ui_badge = "🟢 Shortlisted"
        elif ui_badge == "Manual Review":
            ui_badge = "🟡 Manual Review"
        elif ui_badge == "Rejected":
            ui_badge = "🔴 Rejected"
        st.markdown(f"**Hiring Verdict:**\n### {ui_badge}")
        
    # Render structured diagnostic items or color codes cards layouts safely
    st.markdown("#### 🧠 AI Evaluation Summary Overview")
    st.markdown(
        f"""> 📋 **Executive Fit Summary:**
        > {res['AI Summary']}"""
    )
    
    col_g, col_r = st.columns(2)
    with col_g:
        st.markdown("**🟢 Identified Overlapping Match Skills:**")
        if res["Matching Skills"]:
            st.write(", ".join([f"`{s}`" for s in res["Matching Skills"]]))
        else:
            st.caption("No matching skills found.")
    with col_r:
        st.markdown("**🔴 Missing Role Priority Requirements:**")
        if res["Missing Skills"]:
            # Display colored warnings inline blocks using basic markup tags
            st.markdown(", ".join([f"<span style='color:#DC2626; font-weight:bold;'>{s}</span>" for s in res["Missing Skills"]]), unsafe_allow_html=True)
        else:
            st.caption("No missing criteria found.")

    if res["Potential Concerns"]:
        st.markdown("**⚠️ Flagged Profile Risk and Gaps Indicators:**")
        for concern in res["Potential Concerns"]:
            st.markdown(f"- <span style='color:#D97706;'>{concern}</span>", unsafe_allow_html=True)
            
    st.write(f"**💼 Experience Alignment Context:** {res['Relevant Experience']}")

    st.markdown("---")

    # Display Master Candidate Profile Card information rows blocks parameters layout 
    st.subheader(f"🗂️ Candidate Card Profile Matrix [{res['Candidate ID']}]")
    
    col_info_l, col_info_r = st.columns(2)
    with col_info_l:
        st.write(f"**👤 Full Candidate Name:** {res['Candidate Name']}")
        st.write(f"**📧 Email Address:** {res['Email']}")
        st.write(f"**📞 Primary Phone Line:** {res['Phone']}")
        st.write(f"**📍 Current Location Area:** {res['Location']}")
    with col_info_r:
        st.write(f"**💼 Registered Role Status:** {res['Current Role']}")
        st.write(f"**🏢 Associated Company Office:** {res['Current Company']}")
        st.write(f"**⏱️ Data Pipeline Creation:** `{res['Created Time']}`")
        st.write(f"**📂 Attachment Identifier:** `{res['Resume File']}`")

    with st.expander("📝 View Full Extracted Competency Experience, Projects & Academic History details"):
        st.markdown("**Employment Record Tracks History:**")
        for exp in res["Experience"]:
            if isinstance(exp, dict):
                st.markdown(f"- **{exp.get('Job Title', 'N/A')}** at *{exp.get('Company', 'N/A')}* ({exp.get('Duration', 'N/A')})")
                if exp.get("Description"): st.caption(exp.get("Description"))
            else:
                st.markdown(f"- {exp}")
                
        st.markdown("**Academic Institutions Listings Background:**")
        for edu in res["Education"]:
            if isinstance(edu, dict):
                st.markdown(f"- **{edu.get('Degree', 'N/A')}** — *{edu.get('School/University', 'N/A')}* ({edu.get('Year', 'N/A')})")
            else:
                st.markdown(f"- {edu}")
                
        st.markdown("**Key Managed Engineering Projects:**")
        for proj in res["Projects"]:
            if isinstance(proj, dict):
                st.markdown(f"- **{proj.get('Project Name', 'N/A')}:** {proj.get('Description', 'N/A')}")
            else:
                st.markdown(f"- {proj}")

    st.markdown("---")

    # --- VIEW CANDIDATE DATABASE STABLE PAGE RE-ROUTER INTERACTIVE BUTTON ---
    redirect_button_clicked = st.button("📂 View Candidate Database", use_container_width=True)
    if redirect_button_clicked:
        try:
            st.switch_page("pages/3_Candidate_Database.py")
        except Exception:
            # Drop clean user manual navigation guidance triggers if the current runtime wrapper context rejects switch tasks
            st.info("To inspect the candidate roster matrix grid, simply select the **Candidate Database** tab option in the left side navigation panel area menu.")
