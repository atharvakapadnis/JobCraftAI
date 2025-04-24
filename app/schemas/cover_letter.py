from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ToneType(str, Enum):
    FORMAL = "formal"
    FRIENDLY = "friendly"
    ENTHUSIASTIC = "enthusiastic"
    CONFIDENT = "confident"
    HUMBLE = "humble"
    PROFESSIONAL = "professional"

# Cover letter schemas
class CoverLetterBase(BaseModel):
    job_application_id: str
    tone: Optional[ToneType] = ToneType.PROFESSIONAL

class CoverLetterCreate(CoverLetterBase):
    pass

class CoverLetterUpdate(BaseModel):
    tone: Optional[ToneType] = None
    content: Optional[str] = None
    generation_params: Optional[Dict[str, Any]] = None

class CoverLetter(CoverLetterBase):
    id: str
    content: str
    generation_params: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

# Cover letter generation request schema
class CoverLetterGenerateRequest(BaseModel):
    job_application_id: str
    resume_id: str
    tone: Optional[ToneType] = ToneType.PROFESSIONAL
    emphasized_projects: Optional[List[str]] = None
    emphasized_skills: Optional[List[str]] = None
    emphasized_experiences: Optional[List[str]] = None
    personal_note: Optional[str] = None
    
# Cover letter generation response schema
class CoverLetterGenerateResponse(BaseModel):
    content: str