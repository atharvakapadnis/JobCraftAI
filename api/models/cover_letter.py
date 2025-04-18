from pydantic import BaseModel
from typing import Optional, List

class CoverLetterBase(BaseModel):
    job_application_id: int
    job_description: str
    
class CoverLetterCreate(CoverLetterBase):
    follow_up_answers: Optional[str] = None
    
class CoverLetterResponse(BaseModel):
    cover_letter: str
    job_application_id: int
    cover_letter_id: int
    length: int
    
    class Config:
        from_attributes = True
        
class FollowUpQuestionsResponse(BaseModel):
    follow_up_needed: bool
    questions: List[str]