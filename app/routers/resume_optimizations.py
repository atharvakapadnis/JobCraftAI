from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.job_application import JobApplication
from app.models.resume import Resume
from app.models.resume_optimization import ResumeOptimization, SkillMatch
from app.schemas.resume_optimization import (
    ResumeOptimizationCreate,
    ResumeOptimizationUpdate,
    ResumeOptimization as ResumeOptimizationSchema,
    ResumeOptimizationDetail,
    ResumeOptimizationRequest,
    ResumeOptimizationResponse,
    Suggestion,
    SkillMatch as SkillMatchSchema
)
from app.utils.security import get_current_active_user, generate_uuid
from app.services.resume_optimizer import ResumeOptimizer

router = APIRouter(
    prefix="/resume-optimizations",
    tags=["resume-optimizations"],
    responses={404: {"description": "Not found"}},
)

@router.post("", response_model=ResumeOptimizationSchema, status_code=status.HTTP_201_CREATED)
async def create_resume_optimization(
    optimization: ResumeOptimizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new resume optimization
    """
    # Check if job application exists and belongs to current user
    job_application = db.query(JobApplication).filter(
        JobApplication.id == optimization.job_application_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if job_application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found"
        )
    
    # Check if resume exists and belongs to current user
    resume = db.query(Resume).filter(
        Resume.id == optimization.resume_id,
        Resume.user_id == current_user.id,
        Resume.parsed_status == "completed"
    ).first()
    
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found or not fully parsed"
        )
    
    # Generate optimization suggestions
    optimization_result = await ResumeOptimizer.optimize_resume(
        resume_data=resume.parsed_content,
        job_description=job_application.job_description
    )
    
    # Create resume optimization record
    db_optimization = ResumeOptimization(
        id=generate_uuid(),
        job_application_id=optimization.job_application_id,
        resume_id=optimization.resume_id,
        suggestions=optimization_result["suggestions"],
        match_score=optimization_result.get("match_score")
    )
    
    db.add(db_optimization)
    db.commit()
    db.refresh(db_optimization)
    
    # Add skill matches if available
    if "skill_matches" in optimization_result:
        for match in optimization_result["skill_matches"]:
            skill_match = SkillMatch(
                id=generate_uuid(),
                resume_optimization_id=db_optimization.id,
                skill_name=match["skill_name"],
                is_present=match["is_present"],
                importance=match["importance"],
                suggestion=match.get("suggestion")
            )
            db.add(skill_match)
        
        db.commit()
    
    return db_optimization

@router.get("", response_model=List[ResumeOptimizationSchema])
def get_resume_optimizations(
    job_application_id: Optional[str] = None,
    resume_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get resume optimizations, optionally filtered by job application or resume
    """
    query = db.query(ResumeOptimization).join(
        JobApplication, 
        ResumeOptimization.job_application_id == JobApplication.id
    ).join(
        Resume,
        ResumeOptimization.resume_id == Resume.id
    ).filter(
        JobApplication.user_id == current_user.id,
        Resume.user_id == current_user.id
    )
    
    # Filter by job application if provided
    if job_application_id:
        query = query.filter(ResumeOptimization.job_application_id == job_application_id)
    
    # Filter by resume if provided
    if resume_id:
        query = query.filter(ResumeOptimization.resume_id == resume_id)
    
    # Order by created_at desc
    query = query.order_by(ResumeOptimization.created_at.desc())
    
    return query.all()

@router.get("/{optimization_id}", response_model=ResumeOptimizationDetail)
def get_resume_optimization(
    optimization_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific resume optimization by ID
    """
    optimization = db.query(ResumeOptimization).join(
        JobApplication, 
        ResumeOptimization.job_application_id == JobApplication.id
    ).join(
        Resume,
        ResumeOptimization.resume_id == Resume.id
    ).filter(
        ResumeOptimization.id == optimization_id,
        JobApplication.user_id == current_user.id,
        Resume.user_id == current_user.id
    ).first()
    
    if optimization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume optimization not found"
        )
    
    # Get skill matches
    skill_matches = db.query(SkillMatch).filter(
        SkillMatch.resume_optimization_id == optimization_id
    ).all()
    
    # Build response
    result = ResumeOptimizationDetail.from_orm(optimization)
    result.skill_matches = skill_matches
    
    return result

@router.delete("/{optimization_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume_optimization(
    optimization_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a resume optimization
    """
    optimization = db.query(ResumeOptimization).join(
        JobApplication, 
        ResumeOptimization.job_application_id == JobApplication.id
    ).join(
        Resume,
        ResumeOptimization.resume_id == Resume.id
    ).filter(
        ResumeOptimization.id == optimization_id,
        JobApplication.user_id == current_user.id,
        Resume.user_id == current_user.id
    ).first()
    
    if optimization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume optimization not found"
        )
    
    # Delete resume optimization
    db.delete(optimization)
    db.commit()
    
    return None

@router.post("/optimize", response_model=ResumeOptimizationResponse)
async def optimize_resume(
    request: ResumeOptimizationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate resume optimization suggestions without saving them
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
    
    # Generate optimization suggestions
    optimization_result = await ResumeOptimizer.optimize_resume(
        resume_data=resume.parsed_content,
        job_description=job_application.job_description
    )
    
    return optimization_result