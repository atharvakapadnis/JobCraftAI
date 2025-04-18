from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class JobApplicationBase(BaseModel):
    company: str
    job_title: str
    job_description: str
    
class JobApplicationCreate(JobApplicationBase):
    date_applied: Optional[str] = None
    
class JobApplicationResponse(JobApplicationBase):
    id: int
    date_applied: datetime
    
    class Config:
        from_attributes = True