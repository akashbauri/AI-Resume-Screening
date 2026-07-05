# Import the tools we need to check files, read text, handle formats, and trace execution logs
import os
import logging
import fitz  # This is PyMuPDF, used to open and extract text from PDF files
import docx  # This is python-docx, used to open and extract text from Word files

# Configure standard logging for this service instead of print statements
logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """
    This function opens a PDF file, loops through every single page, 
    and collects all the text inside it.
    
    If the file is corrupt or cannot be opened, it raises an exception 
    so the system knows exactly what went wrong.
    """
    logger.info(f"Starting PDF text extraction for: {file_path}")
    text = ""
    try:
        # Open the PDF document using PyMuPDF
        doc = fitz.open(file_path)
        
        # Look at every page one by one
        for page in doc:
            # Extract the raw text from the current page and add it to our bucket
            text += page.get_text()
            
        # Close the file connection to clean up memory
        doc.close()
        
    except Exception as e:
        logger.error(f"Failed to read PDF file at {file_path}. Error: {str(e)}")
        # If the file is broken, pass the exact error up to the main program
        raise RuntimeError(f"Failed to read PDF file at {file_path}. Error: {str(e)}")
        
    return text

def extract_text_from_docx(file_path: str) -> str:
    """
    This function opens a Microsoft Word (.docx) file, reads every paragraph 
    line by line, and pieces the text back together.
    
    If it fails to open, it raises an exception.
    """
    logger.info(f"Starting DOCX text extraction for: {file_path}")
    text = ""
    try:
        # Open the Word document using python-docx
        doc = docx.Document(file_path)
        
        # Loop through all the paragraphs (blocks of text) in the document
        for paragraph in doc.paragraphs:
            # Gather the text and add a fresh line break at the end of each paragraph
            text += paragraph.text + "\n"
            
    except Exception as e:
        logger.error(f"Failed to read DOCX file at {file_path}. Error: {str(e)}")
        # Pass the file reading error back up to the main program execution
        raise RuntimeError(f"Failed to read DOCX file at {file_path}. Error: {str(e)}")
        
    return text

def extract_text_from_txt(file_path: str) -> str:
    """
    This function opens a plain text (.txt) file using UTF-8 encoding 
    and pulls out the entire textual content stream raw.
    """
    logger.info(f"Starting TXT text extraction for: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read TXT file at {file_path}. Error: {str(e)}")
        raise RuntimeError(f"Failed to read TXT file at {file_path}. Error: {str(e)}")

def normalize_and_clean_text(raw_text: str) -> str:
    """
    This helper function takes messy text, strips out annoying blank lines, 
    and normalizes whitespace so everything is neatly spaced out with 
    exactly one space between words.
    """
    # Split the massive chunk of text into a list of individual lines
    lines = raw_text.splitlines()
    clean_lines = []
    
    for line in lines:
        # .split() automatically clusters words and discards extra tabs, spaces, or gaps
        words = line.split()
        
        # If the line wasn't empty, join its words back together with single spaces
        if words:
            normalized_line = " ".join(words)
            clean_lines.append(normalized_line)
            
    # Join all the clean, normalized lines together using a clear line break separating them
    return "\n".join(clean_lines)

def extract_resume_text(file_path: str) -> str:
    """
    This is the main structural parsing engine wrapper function.
    Give it a file path, and it will check the type, run the extractor, 
    validate content fullness, and return perfectly normalized, plain clean text.
    
    It DOES NOT make any AI calls. It only handles pure file-to-text parsing.
    """
    # 1. Verification Check: Make sure the file actually exists on the computer disk
    if not os.path.exists(file_path):
        logger.error(f"File lookup failed. Path does not exist: '{file_path}'")
        raise FileNotFoundError(f"The resume file was not found at path: '{file_path}'")
        
    # 2. Extract the file extension string (like .pdf, .docx, or .txt) in lowercase letters
    _, file_extension = os.path.splitext(file_path.lower())
    
    raw_extracted_text = ""
    
    # 3. Choose the correct extraction worker based on the file format ending
    if file_extension == ".pdf":
        raw_extracted_text = extract_text_from_pdf(file_path)
        
    elif file_extension == ".docx":
        raw_extracted_text = extract_text_from_docx(file_path)
        
    elif file_extension == ".txt":
        raw_extracted_text = extract_text_from_txt(file_path)
        
    else:
        # If the user tries to feed the engine an unsupported format, reject it immediately
        logger.error(f"Rejected parsing attempt for unsupported file extension: '{file_extension}'")
        raise ValueError(f"Unsupported file format extension: '{file_extension}'. We only support .pdf, .docx, and .txt files.")
        
    # 4. Filter the extracted text to clean up empty spaces, gaps, and blank rows
    final_plain_text = normalize_and_clean_text(raw_extracted_text)
    
    # 5. Empty File Check: Prevent passing un-parsable data payloads upstream to the LLM core services
    if not final_plain_text.strip():
        logger.error(f"Zero text extracted from document context source: '{file_path}'")
        raise ValueError("No readable text could be extracted from the uploaded file.")
        
    logger.info(f"Successfully finished text extraction step for file: '{file_path}'")
    
    # 6. Return the clean plain text string back to the workflow runner
    return final_plain_text
