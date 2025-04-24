from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ApplicationStatus(str, Enum):
    PLANNING = "planning"
    APPLIED = "applied"
    IN_REVIEW = "in_review"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    REJECTED = "rejected"
    OFFER_RECEIVED = "offer_received"
    ACCEPTED = "accepted"
    DECLINED = "declined"

# Requirement schemas
class RequirementBase(BaseModel):
    requirement: str
    type: Optional[str] = None

class RequirementCreate(RequirementBase):
    pass

class Requirement(RequirementBase):
    id: str
    job_application_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

# Responsibility schemas
class ResponsibilityBase(BaseModel):
    responsibility: str

class ResponsibilityCreate(ResponsibilityBase):
    pass

class Responsibility(ResponsibilityBase):
    id: str
    job_application_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

# Job Application schemas
class JobApplicationBase(BaseModel):
    job_title: str
    company_name: str
    job_description: str
    job_url: Optional[str] = None
    job_location: Optional[str] = None
    salary_range: Optional[str] = None

class JobApplicationCreate(JobApplicationBase):
    pass

class JobApplicationUpdate(BaseModel):
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    job_description: Optional[str] = None
    job_url: Optional[str] = None
    job_location: Optional[str] = None
    salary_range: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    applied_date: Optional[datetime] = None
    notes: Optional[str] = None
    parsed_job_details: Optional[Dict[str, Any]] = None

class JobApplication(JobApplicationBase):
    id: str
    user_id: str
    status: ApplicationStatus
    applied_date: Optional[datetime] = None
    notes: Optional[str] = None
    parsed_job_details: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

class JobApplicationDetail(JobApplication):
    requirements: List[Requirement] = []
    responsibilities: List[Responsibility] = []

# Parsed job details schema
class ParsedJobDetails(BaseModel):
    required_skills: Optional[List[str]] = []
    preferred_skills: Optional[List[str]] = []
    required_experience: Optional[str] = None
    required_education: Optional[str] = None
    responsibilities: Optional[List[str]] = []
    benefits: Optional[List[str]] = []
    application_deadline: Optional[str] = None