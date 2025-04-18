from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.dependencies import get_db
from models.models import JobApplication
from api.models.job_application import JobApplicationCreate, JobApplicationResponse
from services.job_application_service import JobApplicationService

router = APIRouter()

@router.post("/", response_model=JobApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_job_application(job_application: JobApplicationCreate, db: Session = Depends(get_db)):
    service = JobApplicationService(db)
    
    date_applied = None
    if job_application.date_applied:
        try:
            date_applied = datetime.strptime(job_application.date_applied, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD."
            )
    
    return service.create_job_application(
        company=job_application.company,
        job_title=job_application.job_title,
        job_description=job_application.job_description,
        date_applied=date_applied
    )

@router.get("/", response_model=List[JobApplicationResponse])
def get_job_applications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = JobApplicationService(db)
    return service.get_job_applications(skip=skip, limit=limit)

@router.get("/{job_application_id}", response_model=JobApplicationResponse)
def get_job_application(job_application_id: int, db: Session = Depends(get_db)):
    service = JobApplicationService(db)
    job_application = service.get_job_application(job_application_id=job_application_id)
    if job_application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job application with ID {job_application_id} not found"
        )
    return job_application