import streamlit as st
import json
import os

# ----------------------------------------------------
# Page Configuration
# ----------------------------------------------------
st.set_page_config(
    page_title="Upload Job Description",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Upload Job Description")
st.markdown("---")

st.write(
    """
Paste the complete Job Description below.

This Job Description will later be used by the AI to compare
the candidate's resume and generate a Match Score.
"""
)

# ----------------------------------------------------
# Create data folder automatically
# ----------------------------------------------------
DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "job_description.json")

os.makedirs(DATA_FOLDER, exist_ok=True)

# ----------------------------------------------------
# Load previously saved Job Description
# ----------------------------------------------------
saved_jd = ""

if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            saved_jd = data.get("job_description", "")
    except Exception:
        saved_jd = ""

# ----------------------------------------------------
# Job Description Text Area
# ----------------------------------------------------
job_description = st.text_area(
    "Paste Job Description",
    value=saved_jd,
    height=350,
    placeholder="Paste the complete Job Description here..."
)

# ----------------------------------------------------
# Save Button
# ----------------------------------------------------
if st.button("💾 Save Job Description", use_container_width=True):

    if not job_description.strip():
        st.error("Please enter a Job Description.")
        st.stop()

    data = {
        "job_description": job_description
    }

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    st.session_state["job_description"] = job_description

    word_count = len(job_description.split())

    st.success("✅ Job Description saved successfully!")

    st.info(f"Total Words: {word_count}")

# ----------------------------------------------------
# Show Current Status
# ----------------------------------------------------
st.markdown("---")

if os.path.exists(DATA_FILE):
    st.success("✅ A Job Description is currently available.")
else:
    st.warning("⚠️ No Job Description has been saved yet.")
