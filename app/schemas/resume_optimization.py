from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ImportanceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class PresenceStatus(str, Enum):
    YES = "yes"
    NO = "no"
    PARTIAL = "partial"

# Skill match schemas
class SkillMatchBase(BaseModel):
    skill_name: str
    is_present: PresenceStatus
    importance: ImportanceLevel
    suggestion: Optional[str] = None

class SkillMatchCreate(SkillMatchBase):
    resume_optimization_id: str

class SkillMatch(SkillMatchBase):
    id: str
    resume_optimization_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

# Suggestion schema
class Suggestion(BaseModel):
    category: str  # e.g., "skills", "experience", "education", "format"
    content: str
    priority: ImportanceLevel

# Resume optimization schemas
class ResumeOptimizationBase(BaseModel):
    job_application_id: str
    resume_id: str

class ResumeOptimizationCreate(ResumeOptimizationBase):
    pass

class ResumeOptimizationUpdate(BaseModel):
    suggestions: Optional[List[Suggestion]] = None
    match_score: Optional[float] = None

class ResumeOptimization(ResumeOptimizationBase):
    id: str
    suggestions: List[Suggestion]
    match_score: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

class ResumeOptimizationDetail(ResumeOptimization):
    skill_matches: List[SkillMatch] = []

# Resume optimization request schema
class ResumeOptimizationRequest(BaseModel):
    job_application_id: str
    resume_id: str

# Resume optimization response schema
class ResumeOptimizationResponse(BaseModel):
    suggestions: List[Suggestion]
    match_score: float
    skill_matches: Optional[List[SkillMatch]] = None