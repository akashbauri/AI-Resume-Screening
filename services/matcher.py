# Import the tools we need to handle structured JSON data and logging
import json
import logging
from typing import Any

# 3. Import call_llm from services.llm_service
from services.llm_service import call_llm

# 4. Import MATCHER_PROMPT from prompts.matcher_prompt
from prompts.matcher_prompt import MATCHER_PROMPT

# Configure standard logging for this service instead of print statements
logger = logging.getLogger(__name__)

def run_resume_match(resume_json: dict, job_description_text: str) -> dict:
    """
    Compares the candidate's structured Resume JSON against the raw Job Description text.
    It builds a formatted prompt, runs it through the central LLM engine service, cleans
    and converts the output into structured Python JSON, and applies robust backend validation.
    
    Args:
        resume_json (dict): Parsed resume attributes from the applicant profile.
        job_description_text (str): Raw requirements context provided by the hiring manager.
        
    Returns:
        dict: Verified evaluation assessment details map containing metrics, text blocks, and arrays.
    """
    # 5. Build the prompt using MATCHER_PROMPT.format()
    prompt = MATCHER_PROMPT.format(
        resume_json=json.dumps(resume_json, indent=2),
        job_description=job_description_text
    )

    try:
        # 6. Send the prompt through call_llm() without creating separate Groq client structures
        raw_response = call_llm(prompt)
    except Exception as e:
        logger.error(f"LLM matching service transmission failed: {str(e)}")
        return {
            "error": "Failed to communicate with matching engine",
            "raw_response": str(e)
        }

    # 7. Clean the response before parsing JSON block structures
    cleaned_response = (
        raw_response
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    # 8. Convert the response into a Python JSON dictionary, catching parsing glitches gracefully
    try:
        evaluation_data = json.loads(cleaned_response)
    except json.JSONDecodeError as json_err:
        logger.error(f"Failed to parse cleaned LLM response text into valid JSON structure: {json_err}")
        return {
            "error": "Invalid JSON returned by matcher",
            "raw_response": raw_response
        }

    # 9. Validate Match Score constraints and guarantee integer transformations
    try:
        raw_score = evaluation_data.get("Match Score", 0)
        # Attempt converting floats or numeric strings into real integer definitions
        score = int(float(raw_score))
    except (ValueError, TypeError):
        logger.warning(f"Unable to parse non-numeric match score asset. Resetting value to 0 fallback.")
        score = 0

    if score < 0:
        score = 0
    elif score > 100:
        score = 100

    evaluation_data["Match Score"] = score

    # 10. Do NOT trust the AI Recommendation: Overwrite and generate accurate recommendation choices manually
    if score >= 80:
        evaluation_data["Recommendation"] = "Shortlisted"
    elif 60 <= score <= 79:
        evaluation_data["Recommendation"] = "Manual Review"
    else:
        evaluation_data["Recommendation"] = "Rejected"

    # 11. Validate all list fields. If null or flat string text types pop out, normalize to array lists
    list_fields = ["Matching Skills", "Missing Skills", "Potential Concerns"]
    for field in list_fields:
        field_val = evaluation_data.get(field)
        if field_val is None:
            evaluation_data[field] = []
        elif isinstance(field_val, str):
            evaluation_data[field] = [field_val.strip()] if field_val.strip() else []
        elif not isinstance(field_val, list):
            evaluation_data[field] = [str(field_val)]

    # 12. Validate string fields. Ensure missing or empty values always return empty strings
    string_fields = ["Relevant Experience", "AI Summary"]
    for field in string_fields:
        field_val = evaluation_data.get(field)
        if field_val is None:
            evaluation_data[field] = ""
        else:
            evaluation_data[field] = str(field_val).strip()

    return evaluation_data
