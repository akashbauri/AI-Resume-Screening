# Import the official Groq tool so we can talk to their AI servers
from groq import Groq
# Import streamlit so we can securely pull the API key from Streamlit Cloud Secrets
import streamlit as st
import json

def get_groq_client():
    """
    This function checks if your secret Groq API key is saved in Streamlit Secrets.
    If it finds the key, it sets up the active Groq connection worker client.
    """
    # Check if the secret key exists in st.secrets
    if "GROQ_API_KEY" not in st.secrets:
        raise ValueError("Missing GROQ_API_KEY! Please add it to your Streamlit App Secrets.")
    
    # Initialize and return the Groq communication helper using the secret key
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

def parse_resume(text):
    """
    This function takes plain resume text and sends it to the Groq AI brain.
    The AI extracts the details and formats them into a clean JSON structure.
    It catches errors safely so your application does not break down.
    """
    # Define the instruction prompt template that tells the AI exactly how to build the JSON
    prompt = f"""
    You are an expert AI Resume Parser. Extract information from the resume text below and organize it into a strict JSON format.
    Do not include any chat, greetings, explanation, or markdown formatting (like ```json). Return ONLY the raw JSON object string.

    The JSON structure MUST look exactly like this:
    {{
        "Candidate Name": "",
        "Email": "",
        "Phone": "",
        "Experience": [
            {{
                "Job Title": "",
                "Company": "",
                "Duration": "",
                "Description": ""
            }}
        ],
        "Company": "",
        "Education": [
            {{
                "Degree": "",
                "School/University": "",
                "Year": ""
            }}
        ],
        "Skills": [],
        "Projects": [],
        "Languages": [],
        "Certifications": [],
        "LinkedIn": ""
    }}

    Resume text to process:
    {text}
    """

    try:
        # Turn on the Groq engine messenger client connection
        client = get_groq_client()
        
        # Send a request message directly to the remote AI servers
        completion = client.chat.completions.create(
            model="qwen-32b",
            messages=[
                {"role": "system", "content": "You are a professional recruiting assistant that only outputs raw, valid JSON structures without conversational text."},
                {"role": "user", "content": prompt}
            ],
            # 0.0 means the AI stays perfectly accurate, factual, and strictly follows instructions
            temperature=0.0
        )
        
        # Extract the pure string answer response out of the deep API structure
        ai_response_text = completion.choices[0].message.content.strip()
        
        # Convert the flat string text response into an organized Python JSON data dictionary
        parsed_json_data = json.loads(ai_response_text)
        return parsed_json_data
        
    except json.JSONDecodeError as json_err:
        # If the AI accidentally returned extra non-JSON chit-chat text, capture it here
        print(f"Failed to decode AI response into valid JSON: {json_err}")
        return {
            "error": "The AI response was not in a strict JSON format.",
            "raw_response": ai_response_text if 'ai_response_text' in locals() else ""
        }
    except Exception as e:
        # If the internet drops or the API key fails, capture the error safely
        print(f"Groq API Error: {str(e)}")
        return {
            "error": f"Unable to get a response from the AI engine due to: {str(e)}"
        }
