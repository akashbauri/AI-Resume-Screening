import json
import time
import logging
import streamlit as st
from groq import Groq, APITimeoutError, APIConnectionError, APIError

# Import the external prompt template strictly as requested
from prompts.resume_parser_prompt import RESUME_PARSER_PROMPT

# Configure standard logging for this service instead of print statements
logger = logging.getLogger(__name__)

# The specific AI model we are required to use
MODEL_NAME = "qwen/qwen3-32b"

def get_groq_client() -> Groq:
    """
    Retrieves the Groq API key from Streamlit secrets and initializes the client.
    
    Returns:
        Groq: An authenticated Groq client instance.
        
    Raises:
        ValueError: If the GROQ_API_KEY is not found in Streamlit secrets.
    """
    # Check if the required secret exists in the Streamlit configuration
    if "GROQ_API_KEY" not in st.secrets:
        logger.error("GROQ_API_KEY is missing from Streamlit secrets.")
        raise ValueError("Missing GROQ_API_KEY! Please add it to your Streamlit App Secrets.")
    
    # Initialize and return the Groq client
    return Groq(api_key=st.secrets["GROQ_API_KEY"])


def call_llm(prompt: str) -> str:
    """
    Sends a prompt to the Groq LLM with specific parameters, including automatic retries.
    
    Args:
        prompt (str): The text instructions to send to the AI.
        
    Returns:
        str: The raw text response from the AI.
        
    Raises:
        Exception: If the API call fails after maximum retry attempts.
    """
    client = get_groq_client()
    max_attempts = 3
    
    # Try calling the API up to 3 times to handle temporary network or timeout issues
    for attempt in range(max_attempts):
        try:
            logger.info(f"Sending request to Groq API (Attempt {attempt + 1}/{max_attempts})")
            
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                top_p=0.9,
                max_tokens=2048,
                stream=False
            )
            
            # Successfully received response, return the content
            return completion.choices[0].message.content
            
        except (APITimeoutError, APIConnectionError) as network_err:
            # Handle timeout and connection errors gracefully
            logger.warning(f"Network issue during Groq API call (Attempt {attempt + 1}): {network_err}")
            if attempt == max_attempts - 1:
                logger.error("Max retries reached. Groq API is unavailable due to network/timeout.")
                raise network_err
                
        except APIError as api_err:
            # Handle Groq-specific API errors
            logger.warning(f"Groq API returned an error (Attempt {attempt + 1}): {api_err}")
            if attempt == max_attempts - 1:
                logger.error("Max retries reached. Groq API failed.")
                raise api_err
                
        except Exception as e:
            # Handle any other unexpected errors
            logger.warning(f"Unexpected error calling Groq API (Attempt {attempt + 1}): {str(e)}")
            if attempt == max_attempts - 1:
                logger.error("Max retries reached. Groq API call failed unexpectedly.")
                raise e
        
        # Wait a moment before retrying (exponential backoff)
        time.sleep(2 ** attempt)


def parse_resume(resume_text: str) -> dict:
    """
    Processes the raw resume text through the AI to extract structured JSON data.
    
    Args:
        resume_text (str): The raw text extracted from the uploaded resume file.
        
    Returns:
        dict: A dictionary containing the parsed candidate information, or an error dictionary.
    """
    # Build the final prompt securely using the imported template
    prompt = RESUME_PARSER_PROMPT.format(resume_text=resume_text)
    
    try:
        # Get the response text from the LLM
        response_text = call_llm(prompt)
        
    except Exception as e:
        logger.error(f"Failed to extract resume data due to API failure: {str(e)}")
        return {
            "error": "Failed to communicate with LLM",
            "raw_response": str(e)
        }
        
    # Clean up the response text before trying to parse the JSON
    # Remove markdown formatting like ```json and trailing/leading spaces
    cleaned_text = response_text.strip()
    
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[7:]
    elif cleaned_text.startswith("```"):
        cleaned_text = cleaned_text[3:]
        
    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]
        
    cleaned_text = cleaned_text.strip()
    
    # Try converting the cleaned text into a Python dictionary
    try:
        parsed_json_data = json.loads(cleaned_text)
        return parsed_json_data
        
    except json.JSONDecodeError as json_err:
        logger.error(f"Failed to decode LLM response into JSON: {json_err}")
        # Return the exact error structure required
        return {
            "error": "Invalid JSON returned by LLM",
            "raw_response": response_text
        }


def health_check() -> bool:
    """
    Sends a simple 'Hello' prompt to the AI to verify the connection is active.
    
    Returns:
        bool: True if the API responds successfully, False otherwise.
    """
    try:
        logger.info("Performing Groq API health check...")
        response = call_llm("Hello")
        
        # If we got any response back as a string, the connection is healthy
        if isinstance(response, str) and len(response) > 0:
            logger.info("Health check passed.")
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return False
