from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from models.models import JobApplication

class JobApplicationService:
    def __init__(self, db: Session):
        self.db = db
        
    def create_job_application(
        self, 
        company: str, 
        job_title: str, 
        job_description: str,
        date_applied: Optional[datetime] = None
    ) -> JobApplication:
        """Create a new job application."""
        job_app = JobApplication(
            company=company,
            job_title=job_title,
            job_description=job_description,
            date_applied=date_applied or datetime.utcnow()
        )
        
        self.db.add(job_app)
        self.db.commit()
        self.db.refresh(job_app)
        
        return job_app
        
    def get_job_applications(self, skip: int = 0, limit: int = 100) -> List[JobApplication]:
        """Get all job applications with pagination."""
        return self.db.query(JobApplication).offset(skip).limit(limit).all()
        
    def get_job_application(self, job_application_id: int) -> Optional[JobApplication]:
        """Get a job application by ID."""
        return self.db.query(JobApplication).filter(JobApplication.id == job_application_id).first()