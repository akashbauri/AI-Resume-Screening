# 🤖 AI Resume Screening Assistant

> An AI-powered Resume Screening & Recruitment Platform that automates resume parsing, candidate-job matching, recruiter workflow, and interview question generation using Large Language Models (LLMs).

---

# 📌 Overview

AI Resume Screening Assistant helps recruiters reduce manual screening time by automatically extracting resume information, matching candidates against job descriptions, scoring applicants, and generating AI-powered interview questions.

The platform provides an end-to-end recruitment workflow from resume upload to recruiter decision making.

---

# ✨ Key Features

## 📄 Resume Upload

- Upload Resume (PDF)
- Upload Resume (DOCX)
- Upload Resume (TXT)
- Maximum Upload Size: 10 MB
- Automatic File Validation
- Temporary Secure Storage
- Automatic Cleanup after Processing

---

## 📑 Resume Parsing

Powered by:

- Groq API
- Qwen/Qwen3-32B

The AI automatically extracts:

- Candidate Name
- Email
- Phone
- Location
- Current Role
- Current Company
- Complete Experience
- Education
- Technical Skills
- Soft Skills
- Languages
- Certifications
- Projects
- LinkedIn Profile

---

## 🧠 AI Resume Matching

The uploaded resume is matched against the Job Description.

Generated Results include:

- Match Score (0–100)
- Matching Skills
- Missing Skills
- Relevant Experience
- Potential Concerns
- AI Summary
- Hiring Recommendation

Recommendations

- ✅ Shortlisted
- 🟡 Manual Review
- ❌ Rejected

---

# 📊 AI Candidate Scoring

Automatic candidate scoring based on:

- Skills Match
- Experience
- Education
- Technical Fit
- Job Description Similarity
- Overall Compatibility

---

# 💼 Experience Calculator

Automatically calculates

- Total Experience

Supports

- Years
- Months
- Multiple Companies
- Multiple Roles

Displayed throughout the application.

---

# 📂 Candidate Database

Stores every analyzed candidate.

Features

- Candidate ID
- Resume Information
- Match Score
- AI Summary
- Recommendation
- Status
- Resume File Name
- Job Description
- Created Time
- Updated Time

---

# 🔍 Candidate Search

Search by

- Candidate Name
- Email
- Technical Skills
- Soft Skills
- Current Role
- Company

---

# 🎯 Smart Filters

Filter candidates by

- Recommendation
- Status

---

# 📈 Sorting

Sort candidates using

- Highest Match Score
- Candidate Name
- Latest Candidate

---

# 📊 Database Dashboard

Displays

- Total Candidates
- Highest Match Score
- Average Match Score
- Current Database Size

---

# 📥 Export Candidate Database

Export entire database as

- CSV

Features

- UTF-8 Encoding
- Excel Compatible
- Flattened Lists
- Complete Candidate Information

---

# 📋 Candidate Profile

Displays

- Contact Information
- Employment History
- Education
- Technical Skills
- Soft Skills
- Certifications
- Languages
- Projects
- AI Summary
- Match Score
- Total Experience

---

# 📊 Recruiter Dashboard

Provides

- Candidate Overview
- AI Recommendation
- Status Management
- Recruiter Notes
- Candidate Editing

---

# ✏ Recruiter Management

Recruiters can update

- Candidate Name
- Phone
- Location
- Current Role
- Current Company
- Status
- Recruiter Notes

---

# 📌 Candidate Status Workflow

Supported Statuses

- New
- Under Review
- Interview Scheduled
- Hired
- Rejected

---

# 🤖 AI Interview Question Generator

Generates AI interview questions based on

- Resume
- Job Description

Question Categories

### Technical Questions

- 5 Questions

### Behavioral Questions

- 5 Questions

### Project Questions

- 5 Questions

### HR Questions

- 5 Questions

---

# 💾 Interview Question Download

Download generated interview questions as

- JSON

---

# 📊 Progress Tracking

Live progress bar during analysis

Pipeline

Resume Upload

↓

Resume Parsing

↓

Resume Validation

↓

Experience Calculation

↓

Resume Matching

↓

Database Storage

↓

Dashboard Update

---

# 📧 Validation

Automatic

- Email Validation
- Phone Validation

Invalid candidates are rejected before entering the database.

---

# 🔁 Duplicate Candidate Detection

Duplicate detection using

- Email Address

If found

- Existing profile updated
- No duplicate record created

---

# 🆔 Candidate ID Generator

Automatically generates IDs

Example

```
CAND-000001
CAND-000002
CAND-000003
```

---

# 📅 Automatic Timestamps

Every candidate stores

- Created Time
- Updated Time

---

# 📝 AI Summary

Every candidate receives

- Executive Summary
- Skills Analysis
- Risk Assessment
- Recommendation

---

# ⚠ Risk Analysis

AI detects

- Missing Skills
- Skill Gaps
- Missing Experience
- Qualification Issues

---

# 📚 Supported Resume Formats

- PDF
- DOCX
- TXT

---

# 🧠 AI Model

Groq

Model

```
qwen/qwen3-32b
```

---

# 🏗 Project Structure

```
AI-Resume-Screening/

│

├── app.py

│

├── pages/

│   ├── Upload_Resume.py
│   ├── Candidate_Database.py
│   ├── Recruiter_Dashboard.py

│

├── services/

│   ├── database.py
│   ├── llm_service.py
│   ├── matcher.py
│   ├── resume_parser.py
│   ├── validator.py
│   ├── logger.py
│   ├── interview_generator.py
│   ├── experience_calculator.py

│

├── prompts/

│   ├── resume_parser_prompt.py
│   ├── matcher_prompt.py
│   ├── interview_prompt.py

│

├── data/

│   └── candidates.json

│

├── uploads/

│

├── requirements.txt

└── README.md
```

---

# 🛠 Tech Stack

## Frontend

- Streamlit

## Backend

- Python

## AI

- Groq API
- Qwen/Qwen3-32B

## Resume Parsing

- PyMuPDF
- python-docx

## Data Storage

- JSON Database

## Data Processing

- Pandas

---

# 🚀 Workflow

```
Upload Resume

        ↓

Extract Resume Text

        ↓

Resume Parsing (LLM)

        ↓

Validate Email

        ↓

Validate Phone

        ↓

Calculate Total Experience

        ↓

Resume Matching

        ↓

Generate Match Score

        ↓

Generate AI Summary

        ↓

Save Candidate

        ↓

Candidate Database

        ↓

Recruiter Dashboard

        ↓

Generate AI Interview Questions

        ↓

Download Interview Questions
```

---

# 📈 Current Features

- ✅ Resume Upload
- ✅ Resume Parsing
- ✅ Resume Matching
- ✅ AI Candidate Scoring
- ✅ AI Summary
- ✅ Candidate Database
- ✅ Candidate Search
- ✅ Smart Filters
- ✅ Sorting
- ✅ Recruiter Dashboard
- ✅ Candidate Editing
- ✅ Recruiter Notes
- ✅ Candidate Status Management
- ✅ Duplicate Detection
- ✅ Candidate ID Generator
- ✅ Experience Calculator
- ✅ CSV Export
- ✅ Interview Question Generator
- ✅ JSON Download
- ✅ Validation
- ✅ Progress Tracking
- ✅ Automatic Timestamps

---

# 🔮 Future Improvements

- Excel Export (.xlsx)
- PDF Report Generation
- Resume Ranking Leaderboard
- Bulk Resume Upload
- Resume Comparison
- Recruiter Authentication
- Email Notifications
- ATS Integration
- Cloud Database (PostgreSQL / Supabase)
- Analytics Dashboard
- Multi-Job Support

---

# 👨‍💻 Author

**Akash Bauri**

AI Engineer | Python Developer | Generative AI | LLM | RAG | AI Agents

GitHub: https://github.com/akashbauri

LinkedIn: https://www.linkedin.com/in/akash-bauri

---

# 📜 License

This project is licensed under the MIT License.

---

⭐ If you found this project useful, consider giving it a star on GitHub.
