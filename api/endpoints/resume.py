from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session

from app.dependencies import get_db
from api.models.resume import ResumeOptimizationResponse
from services.resume_service import ResumeService
from utils.pdf import extract_text_from_pdf

router = APIRouter()

@router.post("/optimization", response_model=ResumeOptimizationResponse)
async def optimize_resume(
    resume_file: UploadFile = File(...),
    job_application_id: int = Form(...),
    job_description: str = Form(...),
    db: Session = Depends(get_db)
):
    # Extract text from resume PDF
    file_contents = await resume_file.read()
    resume_text = await extract_text_from_pdf(file_contents)
    
    service = ResumeService(db)
    
    result = service.optimize_resume(
        resume_text=resume_text,
        job_application_id=job_application_id,
        job_description=job_description
    )
    
    return result