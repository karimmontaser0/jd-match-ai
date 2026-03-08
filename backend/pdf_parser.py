import pdfplumber
import io

def extract_resume_text(file_bytes):
    text = ""
    # Use BytesIO to treat the raw bytes as a file-like object
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text