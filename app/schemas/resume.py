from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Education schemas
class EducationBase(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

class EducationCreate(EducationBase):
    pass

class Education(EducationBase):
    id: str
    resume_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

# Experience schemas
class ExperienceBase(BaseModel):
    company: str
    title: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

class ExperienceCreate(ExperienceBase):
    pass

class Experience(ExperienceBase):
    id: str
    resume_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

# Skill schemas
class SkillBase(BaseModel):
    name: str
    category: Optional[str] = None

class SkillCreate(SkillBase):
    pass

class Skill(SkillBase):
    id: str
    resume_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

# Project schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    technologies: Optional[List[str]] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: str
    resume_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

# Resume schemas
class ResumeBase(BaseModel):
    file_name: str
    file_type: str

class ResumeCreate(ResumeBase):
    pass

class ResumeUpdate(BaseModel):
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    parsed_status: Optional[str] = None
    parsed_content: Optional[Dict[str, Any]] = None

class Resume(ResumeBase):
    id: str
    user_id: str
    file_path: str
    parsed_status: str
    parsed_content: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

class ParsedResumeContent(BaseModel):
    educations: Optional[List[Education]] = []
    experiences: Optional[List[Experience]] = []
    skills: Optional[List[Skill]] = []
    projects: Optional[List[Project]] = []
    contact_info: Optional[Dict[str, Any]] = {}
    summary: Optional[str] = None