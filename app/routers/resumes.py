from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import json
import os

from app.database import get_db
from app.models.user import User
from app.models.resume import Resume, ParsedEducation, ParsedExperience, ParsedSkill, ParsedProject
from app.schemas.resume import Resume as ResumeSchema, ResumeUpdate, ParsedResumeContent
from app.utils.security import get_current_active_user, generate_uuid
from app.utils.file_handlers import save_upload_file, remove_file
from app.services.resume_parser import ResumeParser

router = APIRouter(
    prefix="/resumes",
    tags=["resumes"],
    responses={404: {"description": "Not found"}},
)

# Background task to parse resume
async def parse_resume_task(db: Session, resume_id: str, file_path: str):
    """
    Background task to parse a resume
    """
    try:
        # Get the resume from the database
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return
        
        # Update resume status to processing
        resume.parsed_status = "processing"
        db.commit()
        
        # Parse the resume
        parsed_data = await ResumeParser.parse_file(file_path)
        
        # Save parsed data
        resume.parsed_content = parsed_data
        resume.parsed_status = "completed"
        
        # Extract and store structured data
        if "education" in parsed_data:
            for edu in parsed_data["education"]:
                parsed_education = ParsedEducation(
                    id=generate_uuid(),
                    resume_id=resume_id,
                    institution=edu.get("institution", ""),
                    degree=edu.get("degree", ""),
                    field_of_study=edu.get("field_of_study"),
                    start_date=edu.get("start_date"),
                    end_date=edu.get("end_date"),
                    description=edu.get("description")
                )
                db.add(parsed_education)
        
        if "experience" in parsed_data:
            for exp in parsed_data["experience"]:
                parsed_experience = ParsedExperience(
                    id=generate_uuid(),
                    resume_id=resume_id,
                    company=exp.get("company", ""),
                    title=exp.get("title", ""),
                    location=exp.get("location"),
                    start_date=exp.get("start_date"),
                    end_date=exp.get("end_date"),
                    description=exp.get("description")
                )
                db.add(parsed_experience)
        
        if "skills" in parsed_data:
            for skill in parsed_data["skills"]:
                parsed_skill = ParsedSkill(
                    id=generate_uuid(),
                    resume_id=resume_id,
                    name=skill.get("name", ""),
                    category=skill.get("category")
                )
                db.add(parsed_skill)
        
        if "projects" in parsed_data:
            for project in parsed_data["projects"]:
                technologies = project.get("technologies", [])
                if technologies:
                    technologies_str = ",".join(technologies)
                else:
                    technologies_str = None
                
                parsed_project = ParsedProject(
                    id=generate_uuid(),
                    resume_id=resume_id,
                    name=project.get("name", ""),
                    description=project.get("description"),
                    start_date=project.get("start_date"),
                    end_date=project.get("end_date"),
                    technologies=technologies_str
                )
                db.add(parsed_project)
        
        db.commit()
    except Exception as e:
        # Update resume status to failed
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if resume:
            resume.parsed_status = "failed"
            db.commit()

@router.post("", response_model=ResumeSchema, status_code=status.HTTP_201_CREATED)
async def create_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a new resume
    """
    try:
        # Save uploaded file
        file_path, file_type = save_upload_file(file, directory="resumes")
        
        # Create resume record
        resume = Resume(
            id=generate_uuid(),
            user_id=current_user.id,
            file_name=file.filename,
            file_path=file_path,
            file_type=file_type,
            parsed_status="pending"
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        # Start background task to parse resume
        background_tasks.add_task(parse_resume_task, db, resume.id, file_path)
        
        return resume
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error uploading resume: {str(e)}"
        )

@router.get("", response_model=List[ResumeSchema])
def get_user_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all resumes for the current user
    """
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    return resumes

@router.get("/{resume_id}", response_model=ResumeSchema)
def get_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific resume by ID
    """
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    return resume

@router.get("/{resume_id}/parsed", response_model=ParsedResumeContent)
def get_parsed_resume_content(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get parsed content of a specific resume
    """
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Check if resume has been parsed
    if resume.parsed_status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resume parsing is not complete. Current status: {resume.parsed_status}"
        )
    
    # Get parsed data
    parsed_content = resume.parsed_content
    
    # Get structured data
    educations = db.query(ParsedEducation).filter(ParsedEducation.resume_id == resume_id).all()
    experiences = db.query(ParsedExperience).filter(ParsedExperience.resume_id == resume_id).all()
    skills = db.query(ParsedSkill).filter(ParsedSkill.resume_id == resume_id).all()
    projects = db.query(ParsedProject).filter(ParsedProject.resume_id == resume_id).all()
    
    # Build response
    return {
        "educations": educations,
        "experiences": experiences,
        "skills": skills,
        "projects": projects,
        "contact_info": parsed_content.get("contact_info", {}),
        "summary": parsed_content.get("summary")
    }

@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a resume
    """
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Delete file
    if resume.file_path and os.path.exists(resume.file_path):
        remove_file(resume.file_path)
    
    # Delete resume record
    db.delete(resume)
    db.commit()
    
    return None