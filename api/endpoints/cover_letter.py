from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies import get_db
from api.models.cover_letter import CoverLetterResponse, FollowUpQuestionsResponse
from services.cover_letter_service import CoverLetterService
from utils.pdf import extract_text_from_pdf

router = APIRouter()

@router.post("/generate", response_model=CoverLetterResponse | FollowUpQuestionsResponse)
async def generate_cover_letter(
    resume_file: UploadFile = File(...),
    job_application_id: int = Form(...),
    job_description: str = Form(...),
    follow_up_answers: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # Extract text from resume PDF
    file_contents = await resume_file.read()
    resume_text = await extract_text_from_pdf(file_contents)
    
    service = CoverLetterService(db)
    
    result = service.generate_cover_letter(
        resume_text=resume_text,
        job_application_id=job_application_id,
        job_description=job_description,
        follow_up_answers=follow_up_answers
    )
    
    return result