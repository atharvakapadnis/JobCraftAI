import io
import logging
from typing import Union
from fastapi import HTTPException
import PyPDF2

logger = logging.getLogger("pdf")

async def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        pdf_bytes: PDF file as bytes
        
    Returns:
        Extracted text as string
    """
    try:
        pdf_stream = io.BytesIO(pdf_bytes)
        reader = PyPDF2.PdfReader(pdf_stream)
        
        extracted_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n\n"
                
        return extracted_text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise HTTPException(
            status_code=400, 
            detail=f"Error extracting text from PDF: {str(e)}"
        )