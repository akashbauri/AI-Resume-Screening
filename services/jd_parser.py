# Import the tools we need to process file formats and file tracks
import os
import fitz  # This is PyMuPDF, used to open and read PDF documents
import docx  # This is python-docx, used to open and read Microsoft Word files

def clean_text_spaces(raw_text):
    """
    This function takes messy text, breaks it down line by line, 
    removes empty lines, and joins it back together smoothly.
    """
    lines = raw_text.splitlines()
    good_lines = []
    
    for line in lines:
        # Strip removes blank spaces from the edges of a line
        cleaned_line = line.strip()
        # Only keep the line if it actually has text inside it
        if cleaned_line != "":
            good_lines.append(cleaned_line)
            
    # Join everything back into a big string block using fresh new lines
    return "\n".join(good_lines)

def parse_job_description(file_path):
    """
    This function looks at a file, reads it based on its type (.pdf, .docx, or .txt), 
    and returns a clean string of the text.
    """
    # Find out what the file ending is (.pdf, .docx, or .txt) in lowercase letters
    _, file_extension = os.path.splitext(file_path.lower())
    extracted_text = ""
    
    try:
        # Case A: If it is a PDF file
        if file_extension == ".pdf":
            doc = fitz.open(file_path)
            for page in doc:
                extracted_text += page.get_text()
            doc.close()
            
        # Case B: If it is a Microsoft Word file
        elif file_extension == ".docx":
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                extracted_text += paragraph.text + "\n"
                
        # Case C: If it is a standard simple flat text file
        elif file_extension == ".txt":
            # Open the file in read mode ('r') using safe universal language encoding (utf-8)
            with open(file_path, "r", encoding="utf-8") as f:
                extracted_text = f.read()
                
        else:
            print(f"Unsupported file format: {file_extension}")
            return ""
            
    except Exception as e:
        print(f"An error occurred while reading the job description file: {e}")
        return ""
        
    # Clean up all the huge empty spaces and blank lines from our text
    return clean_text_spaces(extracted_text)
