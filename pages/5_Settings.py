# Import our web interface, configuration rules, database counters, and log service
import streamlit as st
import os
from config.settings import DEFAULT_MODEL, GROQ_API_KEY
from services.database import load_all_candidates
from services.logger import log_event, LOG_FILE_PATH

# Log that someone visited the settings system screen dashboard panel
log_event("User accessed system configuration settings dashboard screen panel view.", level="info")

st.title("⚙️ System Control & Settings Dashboard")
st.write("Review backend system parameters, core model engine setups, database records counters, and live activity tracking lines below.")

st.markdown("---")

# --- SECTION 1: SYSTEM APPLICATION METRICS PANELS ---
st.subheader("📊 Application Operational Metrics")

# Fetch total candidate count metrics safely out of our local database
candidates_count = len(load_all_candidates())

# Verify if your Groq API key variable is filled or empty string
is_api_key_configured = "🟢 Connected & Active" if GROQ_API_KEY else "🔴 Key Missing / Disconnected"

# Display metrics beautifully using horizontal columns
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Candidates Enrolled", candidates_count)
with col2:
    st.metric("Groq API Connectivity Status", is_api_key_configured)
with col3:
    st.metric("App Project Framework Version", "v1.0.0-Beta")

st.markdown("---")

# --- SECTION 2: CONFIGURATION DETAILS ---
st.subheader("🤖 Artificial Intelligence Configuration")

# Present technical configuration details clearly inside a neat layout frame block
st.write(f"**🧠 Active Large Language Model (LLM):** `{DEFAULT_MODEL}`")
st.write("**🏭 LLM Cloud Infrastructure Host Provider:** `Groq Speed Inference Platform Engine`")

st.markdown("---")

# --- SECTION 3: SYSTEM LOGGER CONSOLE VIEW ---
st.subheader("📜 Live Background System Logs (`logs/app.log`)")

# Check if the log file has been created on the disk yet
if not os.path.exists(LOG_FILE_PATH):
    st.info("No system activity logs have been recorded down onto disk storage yet.")
else:
    try:
        # Read the lines from our live application log file
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            # Grab only the 15 most recent system log lines to show in our preview box
            log_lines = f.readlines()[-15:]
            
        # Join the list back together into a flat string block text paragraph
        full_logs_display_text = "".join(log_lines)
        
        # Display the logs inside a code snippet container box to make it look like a developer console
        st.code(full_logs_display_text, language="text")
        
    except Exception as e:
        st.error(f"Unable to read or parse system tracking logs: {e}")
