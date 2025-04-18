from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from api.models.linkedin import (
    LinkedInRequestCreate, 
    LinkedInRequestResponse,
    JobInquiryCreate,
    JobInquiryResponse
)
from services.linkedin_service import LinkedInService

router = APIRouter()

@router.post("/connection-request", response_model=LinkedInRequestResponse, status_code=status.HTTP_201_CREATED)
def create_linkedin_request(request: LinkedInRequestCreate, db: Session = Depends(get_db)):
    service = LinkedInService(db)
    
    return service.create_linkedin_request(
        name=request.name,
        role=request.role,
        company=request.company,
        about_section=request.about_section
    )

@router.post("/job-inquiry", response_model=JobInquiryResponse, status_code=status.HTTP_201_CREATED)
def create_job_inquiry(request: JobInquiryCreate, db: Session = Depends(get_db)):
    service = LinkedInService(db)
    
    return service.create_job_inquiry(
        job_application_id=request.job_application_id,
        contact_name=request.contact_name,
        contact_role=request.contact_role,
        about_section=request.about_section,
        job_posting=request.job_posting
    )