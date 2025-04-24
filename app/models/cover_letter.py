from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

class CoverLetter(Base):
    __tablename__ = "cover_letters"

    id = Column(String, primary_key=True, index=True)
    job_application_id = Column(String, ForeignKey("job_applications.id"))
    
    # Cover letter details
    content = Column(Text)
    tone = Column(String, nullable=True)  # formal, friendly, enthusiastic, etc.
    
    # Generation parameters
    generation_params = Column(JSON, nullable=True)  # Stores any additional parameters used for generation
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    job_application = relationship("JobApplication", back_populates="cover_letters")