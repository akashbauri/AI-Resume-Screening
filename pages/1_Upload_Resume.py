# Import the tools we need to build our app, handle files, and check dates/times
import streamlit as st
import os
from datetime import datetime

# Define where we want to save our uploaded files on the computer
UPLOAD_FOLDER = "uploads"

# Define the maximum file size allowed: 10 Megabytes (10 * 1024 * 1024 bytes)
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

def setup_upload_directory():
    """
    This function is like building a storage box. 
    It checks if our 'uploads' folder exists. If it is not there, it creates it!
    """
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

def save_uploaded_file(uploaded_file):
    """
    This function takes the file the user gave us, reads it, 
    and writes it down into a real file inside our 'uploads' folder.
    """
    # Create the full path destination name (e.g., 'uploads/my_resume.pdf')
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    
    # Open a blank file in 'write binary' mode (wb) to copy the exact content over
    with open(file_path, "wb") as f:
        # Read the file data the user uploaded and save it into our new folder
        f.write(uploaded_file.getbuffer())
        
    return file_path


# --- START OF THE WEB PAGE ---

# Make sure our 'uploads' folder is ready before we do anything else
setup_upload_directory()

# Give our page a big heading
st.title("📤 Resume Upload Hub")
st.write("Please upload candidate resumes here. We accept PDF and DOCX files up to 10MB.")

# Create the file uploader box where users can drag and drop their resume files
uploaded_file = st.file_uploader(
    label="Choose a resume file from your computer", 
    type=["pdf", "docx"]
)

# Check if the user has actually dropped or selected a file
if uploaded_file is not None:
    
    # Check if the file is too heavy/big (more than 10 Megabytes)
    if uploaded_file.size > MAX_FILE_SIZE_BYTES:
        # Show a red warning box telling them the file is too big!
        st.error(f"❌ This file is too big! The limit is 10MB, but your file is {uploaded_file.size / (1024*1024):.2f}MB.")
    
    else:
        # If the size is safe, save the file using our function from above
        saved_path = save_uploaded_file(uploaded_file)
        
        # Show a green success message letting the user know everything worked out!
        st.success("🎉 File uploaded and saved successfully!")
        
        # Add a thin decorative line to separate the success alert from the file details
        st.markdown("---")
        
        # Create a nice header section to display the metadata details cleanly
        st.subheader("📋 File Metadata Details")
        
        # Convert the raw file size bytes into a human-readable format (Kilobytes)
        file_size_kb = uploaded_file.size / 1024
        
        # Grab the current clock time right now to show when it was uploaded
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Display the file properties nicely using bold text styling
        st.write(f"**📄 File Name:** {uploaded_file.name}")
        st.write(f"**⚖️ Size:** {file_size_kb:.2f} KB")
        st.write(f"**🔤 File Type:** {uploaded_file.type}")
        st.write(f"**⏰ Upload Time:** {current_time}")
