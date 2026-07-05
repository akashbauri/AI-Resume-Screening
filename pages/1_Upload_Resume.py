# Import the tools we need to build our app, handle files, dates, and cross-file tasks
import streamlit as st
import os
from datetime import datetime

# Import our custom backend worker tools matching the exact exported function names
from services.resume_parser import parse_resume
from services.llm_service import parse_resume as parse_resume_to_json
from services.matcher import run_resume_match
from services.database import save_candidate
from services.logger import log_event

# Define where we want to look for temporary uploaded files on our computer
UPLOAD_FOLDER = "uploads"
TEMP_PASTED_JD_FILE = os.path.join(UPLOAD_FOLDER, "temp_pasted_jd.txt")

# Define the maximum file size allowed: 10 Megabytes
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

# --- SESSION STATE INITIALIZATION ---
if "processing_started" not in st.session_state:
    st.session_state.processing_started = False

if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False

# --- COMPONENT LOGIC CHECKS ---
def check_job_description_exists():
    """
    This function looks inside our uploads folder to see if any Job Description file is there.
    It returns True if it finds one, or False if the recruiter hasn't provided a job yet.
    """
    if os.path.exists(UPLOAD_FOLDER):
        for file_name in os.listdir(UPLOAD_FOLDER):
            if "jd_" in file_name or "jd" in file_name:
                return True
    return False

def read_job_description_text():
    """
    This function scans our folder, reads the stored job description text, 
    and returns it as a string so our AI can read it.
    """
    if os.path.exists(UPLOAD_FOLDER):
        for file_name in os.listdir(UPLOAD_FOLDER):
            if "jd" in file_name:
                file_path = os.path.join(UPLOAD_FOLDER, file_name)
                if file_name.endswith(".txt"):
                    with open(file_path, "r", encoding="utf-8") as f:
                        return f.read()
                elif file_name.endswith((".pdf", ".docx")):
                    from services.jd_parser import parse_job_description
                    return parse_job_description(file_path)
    return ""


# --- START OF THE WEB PAGE ---

st.title("📤 Resume Upload & Analysis Hub")
st.write("Upload a candidate's resume to parse details, run the match engine, and save profiles.")

# Create the file uploader box where users can drag and drop their resume files
uploaded_file = st.file_uploader(
    label="Choose a resume file from your computer (PDF or DOCX)", 
    type=["pdf", "docx"]
)

if uploaded_file is not None:
    
    # Enforce our strict 10MB size restriction guardrail check
    if uploaded_file.size > MAX_FILE_SIZE_BYTES:
        st.error(f"❌ This file is too big! The limit is 10MB, but your file is {uploaded_file.size / (1024*1024):.2f}MB.")
    else:
        st.markdown("---")
        st.subheader("📋 Uploaded File Summary")
        file_size_kb = uploaded_file.size / 1024
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        st.write(f"**📄 File Name:** {uploaded_file.name}")
        st.write(f"**⚖️ Size:** {file_size_kb:.2f} KB")
        st.write(f"**🔤 File Type:** {uploaded_file.type}")
        st.write(f"**⏰ Upload Time:** {current_time}")
        
        st.markdown("---")
        
        # Verify if a Job Description exists somewhere in our system folder
        jd_exists = check_job_description_exists()
        
        if not jd_exists:
            st.warning("⚠️ Analysis locked. Please go to the **Job Description** page and add a job profile first!")
            button_disabled_state = True
        elif st.session_state.processing_started:
            button_disabled_state = True
        else:
            st.info("💡 Ready for evaluation! Click the button below to trigger the AI screening worker.")
            button_disabled_state = False

        # --- PRIMARY WORKFLOW BUTTON ---
        analyze_button = st.button(
            label="🚀 Analyze Candidate", 
            disabled=button_disabled_state,
            use_container_width=True
        )
        
        if analyze_button and not st.session_state.processing_started:
            st.session_state.processing_started = True
            st.session_state.analysis_complete = False
            st.rerun()

        if st.session_state.processing_started and not st.session_state.analysis_complete:
            log_event(category="UPLOAD", message=f"Starting automated AI screening pipeline for file: {uploaded_file.name}")
            
            with st.spinner("Processing applicant profile through the AI pipeline... Please wait."):
                
                # Create our visual progress bar animator component
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # --- STEP 1: UPLOADING ---
                status_text.text("🔄 Uploading Resume...")
                progress_bar.progress(15)
                
                temp_resume_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
                with open(temp_resume_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # --- STEP 2: EXTRACTING RAW TEXT ---
                status_text.text("🔄 Extracting Resume...")
                progress_bar.progress(35)
                raw_resume_text = parse_resume(temp_resume_path)
                
                # --- STEP 3: RUNNING AI RESUME PARSING ---
                status_text.text("🧠 Running AI Resume Parsing...")
                progress_bar.progress(55)
                
                # Convert the flat text into our structured parsed JSON profile data dictionary using llm_service
                parsed_json_profile = parse_resume_to_json(raw_resume_text)
                
                if "error" in parsed_json_profile:
                    st.error(f"❌ Resume Parsing Failed: {parsed_json_profile['error']}")
                    st.session_state.processing_started = False
                    st.stop()
                
                # --- STEP 4: AI MATCHER ENGINE ---
                status_text.text("⚡ Matching Resume with Job Description...")
                progress_bar.progress(75)
                
                # Gather our job description text block data
                job_description_text = read_job_description_text()
                
                # Compare both files together using our AI matcher tool
                match_results = run_resume_match(parsed_json_profile, job_description_text)
                
                # --- STEP 5: SAVE INTO DATABASE LAYER ---
                status_text.text("💾 Saving Candidate...")
                progress_bar.progress(90)
                
                # Construct the consolidated final database record mapping matching services/database.py expectations
                candidate_record = {
                    "Candidate Name": parsed_json_profile.get("Candidate Name", "Unknown Applicant"),
                    "Email": parsed_json_profile.get("Email", "N/A"),
                    "Phone": parsed_json_profile.get("Phone", "N/A"),
                    "Location": parsed_json_profile.get("Location", "N/A"),
                    "Current Role": parsed_json_profile.get("Current Role", "N/A"),
                    "Company": parsed_json_profile.get("Current Company", "N/A"),
                    "Experience": parsed_json_profile.get("Experience", []),
                    "Education": parsed_json_profile.get("Education", []),
                    "Technical Skills": parsed_json_profile.get("Technical Skills", []),
                    "Soft Skills": parsed_json_profile.get("Soft Skills", []),
                    "Languages": parsed_json_profile.get("Languages", []),
                    "Projects": parsed_json_profile.get("Projects", []),
                    "Certifications": parsed_json_profile.get("Certifications", []),
                    "Match Score": match_results.get("Match Score", 0),
                    "Matching Skills": match_results.get("Matching Skills", []),
                    "Missing Skills": match_results.get("Missing Skills", []),
                    "Summary": match_results.get("AI Summary", ""),
                    "Recommendation": match_results.get("Recommendation", "Manual Review"),
                    "Status": "Under Review",
                    "Resume File": uploaded_file.name,
                    "Job Description": job_description_text
                }
                
                # Commit record directly into database storage file using save_candidate()
                save_candidate(candidate_record)
                
                # --- STEP 6: FINISHED WORKFLOW ---
                progress_bar.progress(100)
                status_text.text("✅ Completed")
                
                st.session_state.analysis_complete = True
                log_event(category="DATABASE", message=f"Successfully completed AI pipeline screening sequence for candidate: {candidate_record['Candidate Name']}")
                st.rerun()

        if st.session_state.analysis_complete:
            st.session_state.processing_started = False
            
            st.success("🎉 Candidate evaluation complete! AI matching scores and profile details are now synchronized.")
            
            st.markdown("### 🔍 Next Steps:")
            database_redirect_clicked = st.button("📊 View Candidate Database", use_container_width=True)
            
            if database_redirect_clicked:
                st.info("To open up the applicant profiles dashboard matrix list grid, simply click on the **Candidate Database** tab in your left Sidebar menu!")
