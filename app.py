# Import the Streamlit tool so we can build our web page easily
import streamlit as st

# Tell the browser how to set up our page with a title and a wide layout
st.set_page_config(
    page_title="AI Resume Screening Assistant",
    page_icon="💼",
    layout="wide"
)

# Put a big, beautiful title right at the very top of our main webpage
st.title("🤖 AI Resume Screening Assistant")

# Add a thin line under the title to make it look neat and professional
st.markdown("---")

# Open up the sidebar on the left side of the screen to make a navigation menu
with st.sidebar:
    # Put a header inside the sidebar so the user knows what this section is for
    st.header("📍 Navigation Menu")
    
    # Create a group of radio buttons so the user can click and choose only one page at a time
    selected_page = st.radio(
        "Go to page:",
        [
            "Home", 
            "Upload Resume", 
            "Upload Job Description", 
            "Candidate Database", 
            "Recruiter Dashboard", 
            "Settings"
        ]
    )

# Check if the user clicked on the "Home" button in the menu
if selected_page == "Home":
    # Show a welcoming sub-header on the screen
    st.subheader("Welcome to the Smart Recruitment Era!")
    # Write a friendly message explaining what this application does
    st.write("This application helps recruiters look through resumes instantly using artificial intelligence.")

# Check if the user clicked on the "Upload Resume" button
elif selected_page == "Upload Resume":
    # Show a sub-header telling the user what to do here
    st.subheader("📤 Upload Candidate Resumes")
    # Show a box where the user can drag and drop PDF or text files from their computer
    st.file_uploader("Drop resume files here...", type=["pdf", "docx", "txt"])

# Check if the user clicked on the "Upload Job Description" button
elif selected_page == "Upload Job Description":
    # Show a sub-header for the job details page
    st.subheader("📋 Upload Job Description")
    # Show a large box where the user can type or paste the text of a job advertisement
    st.text_area("Paste the requirements for the job opening here:")

# Check if the user clicked on the "Candidate Database" button
elif selected_page == "Candidate Database":
    # Show a sub-header for the database storage view
    st.subheader("🗄️ Candidate Database")
    # Write a message telling the user that their stored files will appear right here
    st.info("Profiles of candidates who have applied will be listed inside this section.")

# Check if the user clicked on the "Recruiter Dashboard" button
elif selected_page == "Recruiter Dashboard":
    # Show a sub-header for the charts and metrics screen
    st.subheader("📊 Recruiter Dashboard")
    # Write a text message showing that scores and charts will live here later
    st.write("Here you will see analytics, matching scores, and AI candidate summaries.")

# Check if the user clicked on the last button called "Settings"
elif selected_page == "Settings":
    # Show a sub-header for configuring settings
    st.subheader("⚙️ System Settings")
    # Create a dropdown box so the user can choose which AI brain model they want to use
    st.selectbox("Select AI Brain Model:", ["Model-Fast-v1", "Model-Smart-v2", "Model-Expert-v3"])
