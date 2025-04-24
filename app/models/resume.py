from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    file_name = Column(String)
    file_path = Column(String)
    file_type = Column(String)  # PDF, DOCX, etc.
    
    # Parsed resume content
    parsed_content = Column(JSON, nullable=True)
    parsed_status = Column(String, default="pending")  # pending, processing, completed, failed
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    optimizations = relationship("ResumeOptimization", back_populates="resume", cascade="all, delete-orphan")

class ParsedEducation(Base):
    __tablename__ = "parsed_educations"
    
    id = Column(String, primary_key=True, index=True)
    resume_id = Column(String, ForeignKey("resumes.id"))
    institution = Column(String)
    degree = Column(String)
    field_of_study = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ParsedExperience(Base):
    __tablename__ = "parsed_experiences"
    
    id = Column(String, primary_key=True, index=True)
    resume_id = Column(String, ForeignKey("resumes.id"))
    company = Column(String)
    title = Column(String)
    location = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ParsedSkill(Base):
    __tablename__ = "parsed_skills"
    
    id = Column(String, primary_key=True, index=True)
    resume_id = Column(String, ForeignKey("resumes.id"))
    name = Column(String)
    category = Column(String, nullable=True)  # technical, soft, language, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ParsedProject(Base):
    __tablename__ = "parsed_projects"
    
    id = Column(String, primary_key=True, index=True)
    resume_id = Column(String, ForeignKey("resumes.id"))
    name = Column(String)
    description = Column(Text, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    technologies = Column(Text, nullable=True)  # Comma-separated values
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())