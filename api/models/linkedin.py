from pydantic import BaseModel, Field
from typing import Optional

class LinkedInRequestBase(BaseModel):
    name: str
    role: str
    company: str
    about_section: Optional[str] = Field(default="")
    
class LinkedInRequestCreate(LinkedInRequestBase):
    pass
    
class LinkedInRequestResponse(LinkedInRequestBase):
    id: int
    message_sent: str
    
    class Config:
        from_attributes = True

class JobInquiryBase(BaseModel):
    job_application_id: int
    contact_name: str
    contact_role: str
    about_section: Optional[str] = Field(default="")
    job_posting: str
    
class JobInquiryCreate(JobInquiryBase):
    pass
    
class JobInquiryResponse(JobInquiryBase):
    id: int
    message_sent: str
    
    class Config:
        from_attributes = True