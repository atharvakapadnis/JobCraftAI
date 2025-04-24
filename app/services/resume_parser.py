import os
import PyPDF2
import docx
from typing import Dict, Any
import io

from app.services.openai_service import OpenAIService

class ResumeParser:
    """
    Service for parsing resume files into structured data
    """
    
    @staticmethod
    async def parse_file(file_path: str) -> Dict[str, Any]:
        """
        Parse a resume file into structured data
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            Structured resume data
        """
        # Extract text from the file
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            resume_text = ResumeParser._extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            resume_text = ResumeParser._extract_text_from_docx(file_path)
        elif file_extension == '.doc':
            # Handling .doc files might require external libraries
            # For now, we'll return an error
            raise ValueError("DOC format is not supported. Please convert to PDF or DOCX.")
        elif file_extension == '.txt':
            resume_text = ResumeParser._extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Use OpenAI to parse the resume text
        parsed_data = await OpenAIService.parse_resume(resume_text)
        
        return parsed_data
    
    @staticmethod
    def _extract_text_from_pdf(file_path: str) -> str:
        """
        Extract text from a PDF file
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text
        """
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise ValueError(f"Error extracting text from PDF: {str(e)}")
        
        return text
    
    @staticmethod
    def _extract_text_from_docx(file_path: str) -> str:
        """
        Extract text from a DOCX file
        
        Args:
            file_path: Path to the DOCX file
            
        Returns:
            Extracted text
        """
        text = ""
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            raise ValueError(f"Error extracting text from DOCX: {str(e)}")
        
        return text
    
    @staticmethod
    def _extract_text_from_txt(file_path: str) -> str:
        """
        Extract text from a TXT file
        
        Args:
            file_path: Path to the TXT file
            
        Returns:
            Extracted text
        """
        text = ""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        except UnicodeDecodeError:
            # Try different encoding if UTF-8 fails
            with open(file_path, 'r', encoding='latin-1') as file:
                text = file.read()
        except Exception as e:
            raise ValueError(f"Error extracting text from TXT: {str(e)}")
        
        return text