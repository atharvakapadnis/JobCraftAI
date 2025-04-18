from pydantic import BaseModel
from typing import Optional

class ResumeOptimizationBase(BaseModel):
    job_application_id: int
    job_description: str
    
class ResumeOptimizationResponse(BaseModel):
    suggestions: str
    job_application_id: int
    resume_suggestion_id: int
    
    class Config:
        from_attributes = True