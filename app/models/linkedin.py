from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.job_application import JobApplication  # Import instead of redefining

class LinkedInMessage(Base):
    __tablename__ = "linkedin_messages"

    id = Column(String, primary_key=True, index=True)
    job_application_id = Column(String, ForeignKey("job_applications.id"))
    
    # Target person details
    target_name = Column(String)
    target_title = Column(String, nullable=True)
    target_company = Column(String, nullable=True)
    about_section = Column(Text, nullable=True)
    
    # Message details
    message_type = Column(String)  # connection_request, job_inquiry
    generated_message = Column(Text)
    character_count = Column(Integer)
    is_sent = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    job_application = relationship("JobApplication", back_populates="linkedin_messages")