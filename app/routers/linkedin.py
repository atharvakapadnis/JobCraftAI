from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.job_application import JobApplication
from app.models.linkedin import LinkedInMessage
from app.schemas.linkedin import (
    LinkedInMessageCreate,
    LinkedInMessageUpdate,
    LinkedInMessage as LinkedInMessageSchema,
    LinkedInMessageGenerateRequest,
    LinkedInMessageGenerateResponse,
    MessageType
)
from app.utils.security import get_current_active_user, generate_uuid
from app.services.linkedin_generator import LinkedInGenerator

router = APIRouter(
    prefix="/linkedin",
    tags=["linkedin"],
    responses={404: {"description": "Not found"}},
)

@router.post("", response_model=LinkedInMessageSchema, status_code=status.HTTP_201_CREATED)
async def create_linkedin_message(
    linkedin_message: LinkedInMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new LinkedIn message
    """
    # Check if job application exists and belongs to current user
    job_application = db.query(JobApplication).filter(
        JobApplication.id == linkedin_message.job_application_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if job_application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found"
        )
    
    # Generate message
    if linkedin_message.message_type == MessageType.CONNECTION_REQUEST:
        message_result = await LinkedInGenerator.generate_connection_request(
            name=linkedin_message.target_name,
            about_section=linkedin_message.about_section,
            title=linkedin_message.target_title,
            company=linkedin_message.target_company
        )
    else:  # JOB_INQUIRY
        message_result = await LinkedInGenerator.generate_job_inquiry(
            name=linkedin_message.target_name,
            job_title=job_application.job_title,
            company_name=job_application.company_name,
            about_section=linkedin_message.about_section,
            title=linkedin_message.target_title,
            company=linkedin_message.target_company,
            job_description=job_application.job_description
        )
    
    # Create LinkedIn message record
    db_linkedin_message = LinkedInMessage(
        id=generate_uuid(),
        job_application_id=linkedin_message.job_application_id,
        target_name=linkedin_message.target_name,
        target_title=linkedin_message.target_title,
        target_company=linkedin_message.target_company,
        about_section=linkedin_message.about_section,
        message_type=linkedin_message.message_type,
        generated_message=message_result["generated_message"],
        character_count=message_result["character_count"],
        is_sent=False
    )
    
    db.add(db_linkedin_message)
    db.commit()
    db.refresh(db_linkedin_message)
    
    return db_linkedin_message

@router.get("", response_model=List[LinkedInMessageSchema])
def get_linkedin_messages(
    job_application_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get LinkedIn messages, optionally filtered by job application
    """
    query = db.query(LinkedInMessage).join(
        JobApplication, 
        LinkedInMessage.job_application_id == JobApplication.id
    ).filter(
        JobApplication.user_id == current_user.id
    )
    
    # Filter by job application if provided
    if job_application_id:
        query = query.filter(LinkedInMessage.job_application_id == job_application_id)
    
    # Order by created_at desc
    query = query.order_by(LinkedInMessage.created_at.desc())
    
    return query.all()

@router.get("/{linkedin_message_id}", response_model=LinkedInMessageSchema)
def get_linkedin_message(
    linkedin_message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific LinkedIn message by ID
    """
    linkedin_message = db.query(LinkedInMessage).join(
        JobApplication, 
        LinkedInMessage.job_application_id == JobApplication.id
    ).filter(
        LinkedInMessage.id == linkedin_message_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if linkedin_message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LinkedIn message not found"
        )
    
    return linkedin_message

@router.put("/{linkedin_message_id}", response_model=LinkedInMessageSchema)
def update_linkedin_message(
    linkedin_message_id: str,
    linkedin_message_update: LinkedInMessageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a LinkedIn message
    """
    linkedin_message = db.query(LinkedInMessage).join(
        JobApplication, 
        LinkedInMessage.job_application_id == JobApplication.id
    ).filter(
        LinkedInMessage.id == linkedin_message_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if linkedin_message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LinkedIn message not found"
        )
    
    # Update LinkedIn message fields
    for key, value in linkedin_message_update.dict(exclude_unset=True).items():
        if value is not None:
            setattr(linkedin_message, key, value)
    
    db.commit()
    db.refresh(linkedin_message)
    
    return linkedin_message

@router.delete("/{linkedin_message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_linkedin_message(
    linkedin_message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a LinkedIn message
    """
    linkedin_message = db.query(LinkedInMessage).join(
        JobApplication, 
        LinkedInMessage.job_application_id == JobApplication.id
    ).filter(
        LinkedInMessage.id == linkedin_message_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if linkedin_message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LinkedIn message not found"
        )
    
    # Delete LinkedIn message
    db.delete(linkedin_message)
    db.commit()
    
    return None

@router.post("/generate", response_model=LinkedInMessageGenerateResponse)
async def generate_linkedin_message(
    request: LinkedInMessageGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a LinkedIn message without saving it
    """
    # Generate message
    if request.message_type == MessageType.CONNECTION_REQUEST:
        message_result = await LinkedInGenerator.generate_connection_request(
            name=request.target_name,
            about_section=request.about_section,
            title=request.target_title,
            company=request.target_company
        )
    else:  # JOB_INQUIRY
        message_result = await LinkedInGenerator.generate_job_inquiry(
            name=request.target_name,
            job_title=request.job_title,
            company_name=request.company_name,
            about_section=request.about_section,
            title=request.target_title,
            company=request.target_company,
            job_description=request.job_description
        )
    
    return message_result

@router.put("/{linkedin_message_id}/mark-sent", response_model=LinkedInMessageSchema)
def mark_linkedin_message_as_sent(
    linkedin_message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mark a LinkedIn message as sent
    """
    linkedin_message = db.query(LinkedInMessage).join(
        JobApplication, 
        LinkedInMessage.job_application_id == JobApplication.id
    ).filter(
        LinkedInMessage.id == linkedin_message_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if linkedin_message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LinkedIn message not found"
        )
    
    # Mark as sent
    linkedin_message.is_sent = True
    db.commit()
    db.refresh(linkedin_message)
    
    return linkedin_message