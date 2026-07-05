# Import the tools we need to read files, handle text patterns, and catch errors
import os
import fitz  # This is PyMuPDF, used to open and read PDF files
import docx  # This is python-docx, used to open and read Microsoft Word files

def extract_text_from_pdf(file_path):
    """
    This function opens a PDF file, goes through it page by page, 
    and extracts all the text inside it.
    
    If the file is broken or cannot be opened, it safely catches the error 
    so our program does not crash.
    """
    text = ""
    try:
        # Open the PDF file using the PyMuPDF library
        doc = fitz.open(file_path)
        
        # Loop through every single page in the PDF document
        for page in doc:
            # Get the text from the current page and append it to our text string
            text += page.get_text()
            
        # Close the document to clean up memory
        doc.close()
        
    except Exception as e:
        # If something goes wrong (like a broken file), print the error and return empty text
        print(f"Error reading PDF file {file_path}: {e}")
        return ""
        
    return text

def extract_text_from_docx(file_path):
    """
    This function opens a DOCX (Word) file, looks at every paragraph line by line, 
    and collects all the text together.
    
    If there is an error, it handles it safely.
    """
    text = ""
    try:
        # Open the Word document using the python-docx library
        doc = docx.Document(file_path)
        
        # Loop through all the paragraphs (blocks of text) in the document
        for paragraph in doc.paragraphs:
            # Add the paragraph text followed by a new line space
            text += paragraph.text + "\n"
            
    except Exception as e:
        # If the file won't open, let us know and safely return empty text
        print(f"Error reading DOCX file {file_path}: {e}")
        return ""
        
    return text

def clean_extracted_text(raw_text):
    """
    This function takes messy text, cleans it up by removing annoying blank lines, 
    and trims extra spaces off the edges so it's easy for our AI to read.
    """
    # Split the big chunk of text into a list of individual lines
    lines = raw_text.splitlines()
    
    # Create an empty list where we will store only the good, filled lines
    clean_lines = []
    
    # Look at each line one by one
    for line in lines:
        # .strip() removes any empty spaces from the left and right sides of the line
        stripped_line = line.strip()
        
        # Only keep the line if it is NOT empty after stripping spaces
        if stripped_line != "":
            clean_lines.append(stripped_line)
            
    # Join all the clean lines back together using a single clear line break
    return "\n".join(clean_lines)

def parse_resume(file_path):
    """
    This is the main brain function! 
    Give it a file path, and it will automatically figure out if it is a PDF 
    or a DOCX file, run the correct parser, and return the beautifully cleaned text.
    """
    # Make sure the file actually exists before we try to open it
    if not os.path.exists(file_path):
        print(f"Error: The file path '{file_path}' does not exist.")
        return ""
        
    # Find out what the file extension is (.pdf or .docx) in lowercase letters
    _, file_extension = os.path.splitext(file_path.lower())
    
    raw_text = ""
    
    # If it is a PDF file, use our PDF function
    if file_extension == ".pdf":
        raw_text = extract_text_from_pdf(file_path)
        
    # If it is a Word file, use our DOCX function
    elif file_extension == ".docx":
        raw_text = extract_text_from_docx(file_path)
        
    # If it is an unsupported file type, let the system know
    else:
        print(f"Unsupported file format: {file_extension}. Only .pdf and .docx are supported.")
        return ""
        
    # Send our messy raw text to the cleaner function to eliminate blank lines
    final_clean_text = clean_extracted_text(raw_text)
    
    return final_clean_text
