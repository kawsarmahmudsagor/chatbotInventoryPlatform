import os
from pathlib import Path
from PyPDF2 import PdfReader
import docx  
import textract 

def pdf_to_text(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def docx_to_text(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def doc_to_text(file_path):
    # textract can handle legacy .doc files
    text = textract.process(file_path).decode("utf-8")
    return text

def convert_to_txt(file_path):
    """
    Converts PDF, DOCX, or DOC files to text.
    Returns the text content as a string.
    """
    ext = Path(file_path).suffix.lower()
    
    if ext == ".pdf":
        text = pdf_to_text(file_path)
    elif ext == ".docx":
        text = docx_to_text(file_path)
    elif ext == ".doc":
        text = doc_to_text(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
    return text

