from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base

class ApplicationStatus(str, enum.Enum):
    PLANNING = "planning"
    APPLIED = "applied"
    IN_REVIEW = "in_review"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    REJECTED = "rejected"
    OFFER_RECEIVED = "offer_received"
    ACCEPTED = "accepted"
    DECLINED = "declined"

class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    
    # Job details
    job_title = Column(String)
    company_name = Column(String)
    job_description = Column(Text)
    job_url = Column(String, nullable=True)
    job_location = Column(String, nullable=True)
    salary_range = Column(String, nullable=True)
    
    # Application details
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.PLANNING)
    applied_date = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Parsed job details (extracted from job description)
    parsed_job_details = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="job_applications")
    linkedin_messages = relationship("LinkedInMessage", back_populates="job_application", cascade="all, delete-orphan")
    cover_letters = relationship("CoverLetter", back_populates="job_application", cascade="all, delete-orphan")
    resume_optimizations = relationship("ResumeOptimization", back_populates="job_application", cascade="all, delete-orphan")

class JobRequirement(Base):
    __tablename__ = "job_requirements"
    
    id = Column(String, primary_key=True, index=True)
    job_application_id = Column(String, ForeignKey("job_applications.id"))
    requirement = Column(Text)
    type = Column(String, nullable=True)  # required, preferred, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class JobResponsibility(Base):
    __tablename__ = "job_responsibilities"
    
    id = Column(String, primary_key=True, index=True)
    job_application_id = Column(String, ForeignKey("job_applications.id"))
    responsibility = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())