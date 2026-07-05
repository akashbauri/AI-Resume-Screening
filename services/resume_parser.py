# Import the tools we need to check files, read text, and handle formats
import os
import fitz  # This is PyMuPDF, used to open and extract text from PDF files
import docx  # This is python-docx, used to open and extract text from Word files

def extract_text_from_pdf(file_path):
    """
    This function opens a PDF file, loops through every single page, 
    and collects all the text inside it.
    
    If the file is corrupt or cannot be opened, it raises an exception 
    so the system knows exactly what went wrong.
    """
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
        # If the file is broken, pass the exact error up to the main program
        raise RuntimeError(f"Failed to read PDF file at {file_path}. Error: {str(e)}")
        
    return text

def extract_text_from_docx(file_path):
    """
    This function opens a Microsoft Word (.docx) file, reads every paragraph 
    line by line, and pieces the text back together.
    
    If it fails to open, it raises an exception.
    """
    text = ""
    try:
        # Open the Word document using python-docx
        doc = docx.Document(file_path)
        
        # Loop through all the paragraphs (blocks of text) in the document
        for paragraph in doc.paragraphs:
            # Gather the text and add a fresh line break at the end of each paragraph
            text += paragraph.text + "\n"
            
    except Exception as e:
        # Pass the file reading error back up to the main program execution
        raise RuntimeError(f"Failed to read DOCX file at {file_path}. Error: {str(e)}")
        
    return text

def normalize_and_clean_text(raw_text):
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

def parse_resume(file_path):
    """
    This is the main structural parsing engine wrapper function.
    Give it a file path, and it will check the type, run the extractor, 
    and return perfectly normalized, plain clean text.
    
    It DOES NOT make any AI calls. It only handles pure file-to-text parsing.
    """
    # 1. Verification Check: Make sure the file actually exists on the computer disk
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The resume file was not found at path: '{file_path}'")
        
    # 2. Extract the file extension string (like .pdf or .docx) in lowercase letters
    _, file_extension = os.path.splitext(file_path.lower())
    
    raw_extracted_text = ""
    
    # 3. Choose the correct extraction worker based on the file format ending
    if file_extension == ".pdf":
        raw_extracted_text = extract_text_from_pdf(file_path)
        
    elif file_extension == ".docx":
        raw_extracted_text = extract_text_from_docx(file_path)
        
    else:
        # If the user tries to feed the engine an image or an excel file, reject it immediately
        raise ValueError(f"Unsupported file format extension: '{file_extension}'. We only support .pdf and .docx files.")
        
    # 4. Filter the extracted text to clean up empty spaces, gaps, and blank rows
    final_plain_text = normalize_and_clean_text(raw_extracted_text)
    
    # 5. Return the clean plain text string back to the workflow runner
    return final_plain_text
