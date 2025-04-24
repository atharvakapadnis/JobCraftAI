from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.job_application import JobApplication, JobRequirement, JobResponsibility, ApplicationStatus
from app.schemas.job_application import (
    JobApplicationCreate, 
    JobApplicationUpdate, 
    JobApplication as JobApplicationSchema,
    JobApplicationDetail,
    ParsedJobDetails
)
from app.utils.security import get_current_active_user, generate_uuid
from app.services.openai_service import OpenAIService

router = APIRouter(
    prefix="/job-applications",
    tags=["job-applications"],
    responses={404: {"description": "Not found"}},
)

# Background task to parse job description
async def parse_job_description_task(db: Session, job_application_id: str, job_description: str):
    """
    Background task to parse a job description
    """
    try:
        # Get the job application from the database
        job_application = db.query(JobApplication).filter(JobApplication.id == job_application_id).first()
        if not job_application:
            return
        
        # Parse the job description
        parsed_data = await OpenAIService.parse_job_description(job_description)
        
        # Save parsed data
        job_application.parsed_job_details = parsed_data
        
        # Extract and store structured data
        if "required_skills" in parsed_data:
            for skill in parsed_data["required_skills"]:
                requirement = JobRequirement(
                    id=generate_uuid(),
                    job_application_id=job_application_id,
                    requirement=skill,
                    type="required"
                )
                db.add(requirement)
        
        if "preferred_skills" in parsed_data:
            for skill in parsed_data["preferred_skills"]:
                requirement = JobRequirement(
                    id=generate_uuid(),
                    job_application_id=job_application_id,
                    requirement=skill,
                    type="preferred"
                )
                db.add(requirement)
        
        if "responsibilities" in parsed_data:
            for resp in parsed_data["responsibilities"]:
                responsibility = JobResponsibility(
                    id=generate_uuid(),
                    job_application_id=job_application_id,
                    responsibility=resp
                )
                db.add(responsibility)
        
        db.commit()
    except Exception as e:
        # Just log the error and continue
        print(f"Error parsing job description: {str(e)}")

@router.post("", response_model=JobApplicationSchema, status_code=status.HTTP_201_CREATED)
async def create_job_application(
    job_application: JobApplicationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new job application
    """
    # Create job application record
    db_job_application = JobApplication(
        id=generate_uuid(),
        user_id=current_user.id,
        job_title=job_application.job_title,
        company_name=job_application.company_name,
        job_description=job_application.job_description,
        job_url=job_application.job_url,
        job_location=job_application.job_location,
        salary_range=job_application.salary_range,
        status=ApplicationStatus.PLANNING
    )
    db.add(db_job_application)
    db.commit()
    db.refresh(db_job_application)
    
    # Start background task to parse job description
    background_tasks.add_task(
        parse_job_description_task, 
        db, 
        db_job_application.id, 
        job_application.job_description
    )
    
    return db_job_application

@router.get("", response_model=List[JobApplicationSchema])
def get_job_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    status: ApplicationStatus = None
):
    """
    Get all job applications for the current user
    """
    query = db.query(JobApplication).filter(JobApplication.user_id == current_user.id)
    
    # Filter by status if provided
    if status:
        query = query.filter(JobApplication.status == status)
    
    # Order by created_at desc
    query = query.order_by(JobApplication.created_at.desc())
    
    return query.all()

@router.get("/{job_application_id}", response_model=JobApplicationDetail)
def get_job_application(
    job_application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific job application by ID
    """
    job_application = db.query(JobApplication).filter(
        JobApplication.id == job_application_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if job_application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found"
        )
    
    # Get requirements and responsibilities
    requirements = db.query(JobRequirement).filter(
        JobRequirement.job_application_id == job_application_id
    ).all()
    
    responsibilities = db.query(JobResponsibility).filter(
        JobResponsibility.job_application_id == job_application_id
    ).all()
    
    # Build response
    result = JobApplicationDetail.from_orm(job_application)
    result.requirements = requirements
    result.responsibilities = responsibilities
    
    return result

@router.put("/{job_application_id}", response_model=JobApplicationSchema)
def update_job_application(
    job_application_id: str,
    job_application_update: JobApplicationUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a job application
    """
    db_job_application = db.query(JobApplication).filter(
        JobApplication.id == job_application_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if db_job_application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found"
        )
    
    # Check if job description is being updated
    reparse_needed = False
    if job_application_update.job_description and job_application_update.job_description != db_job_application.job_description:
        reparse_needed = True
    
    # Update job application fields
    for key, value in job_application_update.dict(exclude_unset=True).items():
        if value is not None:
            setattr(db_job_application, key, value)
    
    # If status is being updated to "applied", set applied_date
    if job_application_update.status == ApplicationStatus.APPLIED and db_job_application.applied_date is None:
        db_job_application.applied_date = datetime.now()
    
    db.commit()
    db.refresh(db_job_application)
    
    # If job description was updated, reparse it
    if reparse_needed:
        background_tasks.add_task(
            parse_job_description_task, 
            db, 
            db_job_application.id, 
            db_job_application.job_description
        )
    
    return db_job_application

@router.delete("/{job_application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_application(
    job_application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a job application
    """
    db_job_application = db.query(JobApplication).filter(
        JobApplication.id == job_application_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if db_job_application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found"
        )
    
    # Delete job application
    db.delete(db_job_application)
    db.commit()
    
    return None

@router.get("/{job_application_id}/parsed", response_model=ParsedJobDetails)
def get_parsed_job_details(
    job_application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get parsed details of a job description
    """
    job_application = db.query(JobApplication).filter(
        JobApplication.id == job_application_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if job_application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found"
        )
    
    # Check if job description has been parsed
    if not job_application.parsed_job_details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description has not been parsed yet"
        )
    
    return job_application.parsed_job_details