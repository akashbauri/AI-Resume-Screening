# Import our web interface builder, pandas tables, and our database tools
import streamlit as st
import pandas as pd
from services.database import load_all_candidates

# Set up the title header for our database page view
st.title("🗄️ Candidate Profiles Database")
st.write("Review all parsed applicants, their matching engine scores, and current statuses below.")

# Load all our current candidate records from our local database system
candidates_data = load_all_candidates()

# Check if we have zero candidates in our database file
if not candidates_data:
    st.info("ℹ️ No candidates found in the database yet. Go upload a resume to populate this area!")
else:
    # 1. Convert our raw Python records list into a clean Pandas DataFrame table object
    df = pd.DataFrame(candidates_data)
    
    # 2. Clean up how lists are displayed (like turning ['Python', 'SQL'] into 'Python, SQL')
    if "Skills" in df.columns:
        df["Skills"] = df["Skills"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
        
    # 3. Define the exact columns we want to expose on our dashboard grid screen
    desired_columns = [
        "Candidate Name", 
        "Email", 
        "Phone", 
        "Skills", 
        "Score", 
        "Recommendation", 
        "Status", 
        "Resume"
    ]
    
    # Only keep columns that actually exist inside our data dictionary records
    display_columns = [col for col in desired_columns if col in df.columns]
    final_df = df[display_columns]
    
    # 4. Add a quick metrics bar summary counter at the top of the grid view
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Applicants", len(final_df))
    with col2:
        # Find the highest profile score achieved inside the dataset matrix
        high_score = final_df["Score"].max() if "Score" in final_df.columns else 0
        st.metric("Highest Match Score", f"{high_score}%")
    with col3:
        st.metric("Storage Mode", "Local JSON Layer")
        
    st.markdown("---")
    
    # 5. Display our final organized table grid perfectly using Streamlit's native data table view
    st.dataframe(
        final_df, 
        use_container_width=True, # Stretch the table to fill the screen width beautifully
        hide_index=True           # Hide the row counter numbers on the far left edge
    )
