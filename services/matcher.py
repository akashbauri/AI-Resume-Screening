# Import the official Groq tool to communicate with the AI servers
from groq import Groq
# Import streamlit to securely read the API key from Streamlit Cloud Secrets
import streamlit as st
import json

def get_groq_client():
    """
    This function initializes and returns the Groq client.
    It fetches the secret key safely from Streamlit Secrets.
    """
    if "GROQ_API_KEY" not in st.secrets:
        raise ValueError("Missing GROQ_API_KEY! Please add it to your Streamlit App Secrets.")
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

def run_resume_match(resume_json, job_description_text):
    """
    This function takes parsed resume JSON data and compares it against 
    the raw Job Description text using the Groq AI engine.
    
    It outputs a beautifully structured Python dictionary with scores, skills gap breakdown, 
    and evaluation metrics without returning any markdown formatting.
    """
    # Convert the incoming resume JSON dictionary into a clean text string for the prompt
    resume_string = json.dumps(resume_json, indent=2)

    # Define the precise instructions telling the AI to calculate the match details
    prompt = f"""
    You are an expert technical recruiter. Compare the candidate's structured Resume JSON against the provided Job Description (JD).
    Analyze both profiles and generate a detailed matching assessment matching the exact JSON schema below.
    
    Do not include any chat, greetings, explanation, or markdown code block formatting (such as ```json). 
    Return ONLY the raw JSON object string.

    The JSON structure MUST look exactly like this:
    {{
        "Match Score": 0,
        "Matching Skills": [],
        "Missing Skills": [],
        "Relevant Experience": "",
        "Potential Concerns": [],
        "AI Summary": "",
        "Recommendation": ""
    }}

    Rules for fields:
    1. "Match Score": An integer value between 0 and 100 representing job fit compatibility.
    2. "Matching Skills": A list of skills found in both the resume data and the job description.
    3. "Missing Skills": Critical requirements from the job description that the candidate lacks.
    4. "Relevant Experience": A brief sentence summarizing how the candidate's history aligns with this role.
    5. "Potential Concerns": A list of gaps, missing certifications, or profile anomalies.
    6. "AI Summary": A clear 3-sentence overview evaluation of the candidate's background fit.
    7. "Recommendation": A clear selection action choice (e.g., "Strongly Recommend Interview", "Proceed with Caution", or "Reject").

    --- JOB DESCRIPTION ---
    {job_description_text}

    --- CANDIDATE RESUME JSON ---
    {resume_string}
    """

    try:
        # Turn on the Groq engine messenger client connection
        client = get_groq_client()
        
        # Send a request message directly to the remote AI servers
        completion = client.chat.completions.create(
            model="qwen-32b",
            messages=[
                {"role": "system", "content": "You are a professional hiring matcher that outputs strict, raw JSON objects without conversational text or markdown blocks."},
                {"role": "user", "content": prompt}
            ],
            # 0.0 means the AI stays perfectly accurate, factual, and strictly follows instructions
            temperature=0.0
        )
        
        # Extract the pure string answer response out of the deep API structure
        ai_response_text = completion.choices[0].message.content.strip()
        
        # Convert the flat string text response into an organized Python data dictionary
        evaluated_match_data = json.loads(ai_response_text)
        return evaluated_match_data
        
    except json.JSONDecodeError as json_err:
        # Catch formatting issues safely if the AI accidentally returned extra conversational text
        print(f"Failed to decode AI response into valid JSON: {json_err}")
        return {
            "error": "The AI matching engine response was not in a strict JSON format.",
            "raw_response": ai_response_text if 'ai_response_text' in locals() else ""
        }
    except Exception as e:
        # Catch unexpected API connection issues or missing secret key failures safely
        print(f"Groq Matcher API Error: {str(e)}")
        return {
            "error": f"Unable to run candidate comparison match due to: {str(e)}"
        }
