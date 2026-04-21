import os
from pathlib import Path
import PyPDF2
import docx
import pandas as pd
import json
import pytesseract
from PIL import Image
from django.core.exceptions import ValidationError

# Ensure Tesseract is installed and accessible
# For Windows, set the Tesseract path if needed:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_txt(file_path):
    """Extract text from a .txt file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_text_from_pdf(file_path):
    """Extract text from a .pdf file."""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text

def extract_text_from_docx(file_path):
    """Extract text from a .docx file."""
    doc = docx.Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs])

def extract_text_from_csv(file_path):
    """Extract text from a .csv file."""
    df = pd.read_csv(file_path)
    return df.to_string()

def extract_text_from_xlsx(file_path):
    """Extract text from a .xlsx file."""
    df = pd.read_excel(file_path)
    return df.to_string()

def extract_text_from_json(file_path):
    """Extract text from a .json file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return json.dumps(data, indent=4)

def extract_text_from_image(file_path):
    """Extract text from an image using OCR."""
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    image = Image.open(file_path)
    return pytesseract.image_to_string(image)

def extract_text(file_path):
    """Extract text based on file extension."""
    extension = Path(file_path).suffix.lower()

    if extension == '.txt':
        return extract_text_from_txt(file_path)
    elif extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif extension == '.docx':
        return extract_text_from_docx(file_path)
    elif extension == '.csv':
        return extract_text_from_csv(file_path)
    elif extension == '.xlsx':
        return extract_text_from_xlsx(file_path)
    elif extension == '.json':
        return extract_text_from_json(file_path)
    elif extension in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
        return extract_text_from_image(file_path)
    else:
        raise ValidationError(f"Unsupported file type: {extension}")