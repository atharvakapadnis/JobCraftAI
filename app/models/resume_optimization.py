from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

class ResumeOptimization(Base):
    __tablename__ = "resume_optimizations"

    id = Column(String, primary_key=True, index=True)
    job_application_id = Column(String, ForeignKey("job_applications.id"))
    resume_id = Column(String, ForeignKey("resumes.id"))
    
    # Optimization details
    suggestions = Column(JSON)  # List of suggestions for resume improvement
    match_score = Column(Float, nullable=True)  # Overall match score (0-1)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    job_application = relationship("JobApplication", back_populates="resume_optimizations")
    resume = relationship("Resume", back_populates="optimizations")

class SkillMatch(Base):
    __tablename__ = "skill_matches"
    
    id = Column(String, primary_key=True, index=True)
    resume_optimization_id = Column(String, ForeignKey("resume_optimizations.id"))
    
    skill_name = Column(String)
    is_present = Column(String)  # yes, no, partial
    importance = Column(String)  # high, medium, low
    suggestion = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())