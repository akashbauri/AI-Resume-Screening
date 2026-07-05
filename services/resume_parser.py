# Import the tools we need to read files, clean up text, and talk to our AI service
import os
import fitz  # This is PyMuPDF, used to open and read PDF files
import docx  # This is python-docx, used to open and read Microsoft Word files
import json  # This helps us check if the AI gave us a perfect data structure block
from services.llm_service import ask_llm
from prompts.resume_parser_prompt import RESUME_PARSER_PROMPT_TEMPLATE

def extract_text_from_pdf(file_path):
    """
    This function opens a PDF file, goes through it page by page, 
    and extracts all the text inside it.
    """
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"Error reading PDF file {file_path}: {e}")
        return ""
    return text

def extract_text_from_docx(file_path):
    """
    This function opens a DOCX (Word) file, looks at every paragraph line by line, 
    and collects all the text together.
    """
    text = ""
    try:
        doc = docx.Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX file {file_path}: {e}")
        return ""
    return text

def clean_extracted_text(raw_text):
    """
    This function takes messy text, cleans it up by removing annoying blank lines, 
    and trims extra spaces off the edges.
    """
    lines = raw_text.splitlines()
    clean_lines = []
    for line in lines:
        stripped_line = line.strip()
        if stripped_line != "":
            clean_lines.append(stripped_line)
    return "\n".join(clean_lines)

def parse_resume_to_json(file_path):
    """
    This is our smart function! 
    It reads a document file, extracts the clean text, hands it over to the 
    Groq AI service with our special prompt, and returns a verified JSON object.
    """
    # 1. Check if the file is real and exists on the disk
    if not os.path.exists(file_path):
        return {"error": "File path does not exist"}
        
    # 2. Extract the file extension to decide how to read it
    _, file_extension = os.path.splitext(file_path.lower())
    raw_text = ""
    
    if file_extension == ".pdf":
        raw_text = extract_text_from_pdf(file_path)
    elif file_extension == ".docx":
        raw_text = extract_text_from_docx(file_path)
    else:
        return {"error": f"Unsupported file type: {file_extension}"}
        
    # 3. Clean up the text to remove huge empty gaps
    clean_text = clean_extracted_text(raw_text)
    if not clean_text:
        return {"error": "Could not extract any text from this file"}
        
    # 4. Fill our prompt template instructions with the clean text we just read
    formatted_prompt = RESUME_PARSER_PROMPT_TEMPLATE.format(resume_text=clean_text)
    
    # 5. Ask our Groq AI service to extract the details and convert it to JSON formatting
    ai_raw_response = ask_llm(formatted_prompt)
    
    # 6. Verify that the AI gave us true JSON data structure back
    try:
        # json.loads converts a plain string block back into a structured Python dictionary
        parsed_json_data = json.loads(ai_raw_response)
        return parsed_json_data
        
    except Exception as e:
        # If the AI accidentally added extra non-JSON chit-chat text, return a fallback error record
        print(f"Failed to decode AI response into valid JSON: {e}")
        return {
            "error": "AI response was not in strict JSON format",
            "raw_response": ai_raw_response
        }
