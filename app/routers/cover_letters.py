from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.job_application import JobApplication
from app.models.resume import Resume
from app.models.cover_letter import CoverLetter
from app.schemas.cover_letter import (
    CoverLetterCreate,
    CoverLetterUpdate,
    CoverLetter as CoverLetterSchema,
    CoverLetterGenerateRequest,
    CoverLetterGenerateResponse,
    ToneType
)
from app.utils.security import get_current_active_user, generate_uuid
from app.services.cover_letter_generator import CoverLetterGenerator

router = APIRouter(
    prefix="/cover-letters",
    tags=["cover-letters"],
    responses={404: {"description": "Not found"}},
)

@router.post("", response_model=CoverLetterSchema, status_code=status.HTTP_201_CREATED)
async def create_cover_letter(
    cover_letter: CoverLetterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new cover letter
    """
    # Check if job application exists and belongs to current user
    job_application = db.query(JobApplication).filter(
        JobApplication.id == cover_letter.job_application_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if job_application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found"
        )
    
    # Get the latest resume for the user
    resume = db.query(Resume).filter(
        Resume.user_id == current_user.id,
        Resume.parsed_status == "completed"
    ).order_by(Resume.created_at.desc()).first()
    
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No parsed resume found. Please upload and parse a resume first."
        )
    
    # Get resume data
    resume_data = resume.parsed_content
    
    # Generate cover letter
    content = await CoverLetterGenerator.generate_cover_letter(
        resume_data=resume_data,
        job_description=job_application.job_description,
        company_name=job_application.company_name,
        job_title=job_application.job_title,
        tone=cover_letter.tone.value if cover_letter.tone else "professional",
        portfolio_url=current_user.portfolio_url
    )
    
    # Create cover letter record
    db_cover_letter = CoverLetter(
        id=generate_uuid(),
        job_application_id=cover_letter.job_application_id,
        tone=cover_letter.tone,
        content=content,
        generation_params={
            "resume_id": resume.id,
            "portfolio_url": current_user.portfolio_url,
            "emphasized_projects": None,
            "emphasized_skills": None,
            "emphasized_experiences": None,
            "personal_note": None
        }
    )
    
    db.add(db_cover_letter)
    db.commit()
    db.refresh(db_cover_letter)
    
    return db_cover_letter

@router.get("", response_model=List[CoverLetterSchema])
def get_cover_letters(
    job_application_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get cover letters, optionally filtered by job application
    """
    query = db.query(CoverLetter).join(
        JobApplication, 
        CoverLetter.job_application_id == JobApplication.id
    ).filter(
        JobApplication.user_id == current_user.id
    )
    
    # Filter by job application if provided
    if job_application_id:
        query = query.filter(CoverLetter.job_application_id == job_application_id)
    
    # Order by created_at desc
    query = query.order_by(CoverLetter.created_at.desc())
    
    return query.all()

@router.get("/{cover_letter_id}", response_model=CoverLetterSchema)
def get_cover_letter(
    cover_letter_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific cover letter by ID
    """
    cover_letter = db.query(CoverLetter).join(
        JobApplication, 
        CoverLetter.job_application_id == JobApplication.id
    ).filter(
        CoverLetter.id == cover_letter_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if cover_letter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cover letter not found"
        )
    
    return cover_letter

@router.put("/{cover_letter_id}", response_model=CoverLetterSchema)
def update_cover_letter(
    cover_letter_id: str,
    cover_letter_update: CoverLetterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a cover letter
    """
    cover_letter = db.query(CoverLetter).join(
        JobApplication, 
        CoverLetter.job_application_id == JobApplication.id
    ).filter(
        CoverLetter.id == cover_letter_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if cover_letter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cover letter not found"
        )
    
    # Update cover letter fields
    for key, value in cover_letter_update.dict(exclude_unset=True).items():
        if value is not None:
            setattr(cover_letter, key, value)
    
    db.commit()
    db.refresh(cover_letter)
    
    return cover_letter

@router.delete("/{cover_letter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cover_letter(
    cover_letter_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a cover letter
    """
    cover_letter = db.query(CoverLetter).join(
        JobApplication, 
        CoverLetter.job_application_id == JobApplication.id
    ).filter(
        CoverLetter.id == cover_letter_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if cover_letter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cover letter not found"
        )
    
    # Delete cover letter
    db.delete(cover_letter)
    db.commit()
    
    return None

@router.post("/generate", response_model=CoverLetterGenerateResponse)
async def generate_cover_letter(
    request: CoverLetterGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a cover letter without saving it
    """
    # Check if job application exists and belongs to current user
    job_application = db.query(JobApplication).filter(
        JobApplication.id == request.job_application_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if job_application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found"
        )
    
    # Check if resume exists and belongs to current user
    resume = db.query(Resume).filter(
        Resume.id == request.resume_id,
        Resume.user_id == current_user.id,
        Resume.parsed_status == "completed"
    ).first()
    
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found or not fully parsed"
        )
    
    # Get resume data
    resume_data = resume.parsed_content
    
    # Generate cover letter
    content = await CoverLetterGenerator.generate_cover_letter(
        resume_data=resume_data,
        job_description=job_application.job_description,
        company_name=job_application.company_name,
        job_title=job_application.job_title,
        tone=request.tone.value if request.tone else "professional",
        emphasized_projects=request.emphasized_projects,
        emphasized_skills=request.emphasized_skills,
        emphasized_experiences=request.emphasized_experiences,
        personal_note=request.personal_note,
        portfolio_url=current_user.portfolio_url
    )
    
    return {"content": content}