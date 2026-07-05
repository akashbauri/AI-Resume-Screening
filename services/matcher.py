# Import the tools we need to process data and talk to our AI service
import json
from services.llm_service import ask_llm
from prompts.matcher_prompt import MATCHER_PROMPT_TEMPLATE

def run_resume_match(resume_text, job_description_text):
    """
    This function takes two pieces of clean text: the candidate's resume 
    and the job description requirements.
    
    It combines them into our custom matching prompt, sends it to the AI brain, 
    and outputs a beautiful python dictionary containing the final scores and breakdowns.
    """
    
    # 1. Sanity Check: Make sure both inputs actually have text inside them
    if not resume_text.strip() or not job_description_text.strip():
        return {
            "error": "Cannot perform match because either the resume or job description text is empty."
        }
        
    # 2. Fill our prompt template instructions with the actual text items we want to compare
    formatted_matcher_prompt = MATCHER_PROMPT_TEMPLATE.format(
        resume_text=resume_text,
        job_description_text=job_description_text
    )
    
    # 3. Request our Groq AI service to compare both profiles and output a JSON string answer
    ai_raw_match_response = ask_llm(formatted_matcher_prompt)
    
    # 4. Attempt to verify and decode the AI's answer text into a true structured Python data dictionary
    try:
        # json.loads parses the flat string response back into an organized dictionary
        evaluated_match_data = json.loads(ai_raw_match_response)
        return evaluated_match_data
        
    except Exception as e:
        # If the AI engine returned non-JSON text structure by mistake, catch the failure safely
        print(f"Failed to transform match data into clean JSON format: {e}")
        return {
            "error": "The AI evaluation engine could not produce a strict JSON output.",
            "raw_response": ai_raw_match_response
        }
