import streamlit as st

# -----------------------------------------------------
# Page Configuration
# -----------------------------------------------------
st.set_page_config(
    page_title="AI Resume Screening Assistant",
    page_icon="🤖",
    layout="wide",
)

# -----------------------------------------------------
# Main Title
# -----------------------------------------------------
st.title("🤖 AI Resume Screening Assistant")
st.markdown("---")

# -----------------------------------------------------
# Welcome Section
# -----------------------------------------------------
st.markdown(
    """
# Welcome to the AI Resume Screening Assistant 👋

This application helps recruiters automatically screen resumes using Artificial Intelligence.

## Workflow

1️⃣ Upload Candidate Resume

2️⃣ Upload Job Description

3️⃣ Click **🚀 Analyze Candidate**

4️⃣ AI extracts candidate information

5️⃣ AI compares Resume with Job Description

6️⃣ Match Score is generated

7️⃣ Candidate is saved into the database

8️⃣ Recruiter reviews the candidate

---

## Available Pages

Use the **left sidebar** to navigate through the application.

- 📄 Upload Resume
- 📋 Upload Job Description
- 🗄️ Candidate Database
- 📊 Recruiter Dashboard
- ⚙️ Settings

---

### Features

✅ Resume Parsing

✅ AI Candidate Matching

✅ Match Score Generation

✅ Candidate Database

✅ Recruiter Dashboard

✅ Groq AI Integration

---

### Assignment Workflow

Resume Upload

↓

Job Description

↓

AI Resume Parsing

↓

Resume Matching

↓

Candidate Database

↓

Recruiter Review

↓

Interview Scheduling (Coming Soon)

---

Built using

- Python
- Streamlit
- Groq AI
- FastAPI Ready Architecture
"""
)

st.success("✅ Use the sidebar on the left to start screening candidates.")
