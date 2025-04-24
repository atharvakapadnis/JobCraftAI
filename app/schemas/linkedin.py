from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    CONNECTION_REQUEST = "connection_request"
    JOB_INQUIRY = "job_inquiry"

# LinkedIn message schemas
class LinkedInMessageBase(BaseModel):
    target_name: str
    message_type: MessageType
    about_section: Optional[str] = None
    target_title: Optional[str] = None
    target_company: Optional[str] = None

class LinkedInMessageCreate(LinkedInMessageBase):
    job_application_id: str

class LinkedInMessageUpdate(BaseModel):
    target_name: Optional[str] = None
    target_title: Optional[str] = None
    target_company: Optional[str] = None
    about_section: Optional[str] = None
    message_type: Optional[MessageType] = None
    generated_message: Optional[str] = None
    is_sent: Optional[bool] = None

class LinkedInMessage(LinkedInMessageBase):
    id: str
    job_application_id: str
    generated_message: str
    character_count: int
    is_sent: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

# Message generation request schema
class LinkedInMessageGenerateRequest(BaseModel):
    target_name: str
    message_type: MessageType
    about_section: Optional[str] = None
    target_title: Optional[str] = None
    target_company: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    job_description: Optional[str] = None

# Message generation response schema
class LinkedInMessageGenerateResponse(BaseModel):
    generated_message: str
    character_count: int