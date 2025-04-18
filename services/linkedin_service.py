from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from models.models import Person, JobApplication, JobInquiry
from tools.linkedin_connection import generate_linkedin_connection_request
from tools.job_inquiry import linkedin_job_inquiry_request
from core.rag.retrieval import DocumentRetriever

class LinkedInService:
    def __init__(self, db: Session):
        self.db = db
        self.connection_retriever = DocumentRetriever("linkedin_connections")
        self.inquiry_retriever = DocumentRetriever("job_inquiries")
        
    def create_linkedin_request(
        self, 
        name: str, 
        role: str, 
        company: str,
        about_section: Optional[str] = ""
    ):
        """Generate a LinkedIn connection request and save it to the database."""
        # Check if the job application exists
        
        # Generate the message with RAG context enhancement
        # First, try to retrieve similar messages for context
        similar_messages = self.connection_retriever.retrieve(
            query=f"{name} {role} {company} {about_section}",
            k=3,
            filter={"company": company} if company else None
        )
        
        # Prepare RAG context
        rag_context = ""
        if similar_messages:
            rag_context = "Here are some examples of previous successful connection requests:\n\n"
            for i, msg in enumerate(similar_messages):
                rag_context += f"Example {i+1}: {msg['document']}\n\n"
        
        # Generate the message
        generated_message = generate_linkedin_connection_request(
            name=name, 
            about_section=about_section,
            rag_context=rag_context
        )
        
        # Save to database
        person = Person(
            contact_name=name,
            contact_role=role,
            contact_company=company,
            message_sent=generated_message
        )
        
        self.db.add(person)
        self.db.commit()
        self.db.refresh(person)
        
        # Add to vector store for future RAG
        self.connection_retriever.add_document(
            text=generated_message,
            metadata={
                "person_id": person.id,
                "name": name,
                "role": role,
                "company": company
            }
        )
        
        return {
            "id": person.id,
            "name": name,
            "role": role,
            "company": company,
            "about_section": about_section,
            "message_sent": generated_message
        }
        
    def create_job_inquiry(
        self,
        job_application_id: int,
        contact_name: str,
        contact_role: str,
        about_section: str = "",
        job_posting: str = ""
    ):
        """Generate a LinkedIn job inquiry request and save it to the database."""
        # Check if the job application exists
        job_app = self.db.query(JobApplication).filter(JobApplication.id == job_application_id).first()
        if not job_app:
            raise ValueError(f"Job application with ID {job_application_id} not found")
        
        # Generate the message with RAG context enhancement
        # First, try to retrieve similar messages for context
        similar_messages = self.inquiry_retriever.retrieve(
            query=f"{contact_name} {contact_role} {job_app.job_title} {job_app.company} {about_section}",
            k=3
        )
        
        # Prepare RAG context
        rag_context = ""
        if similar_messages:
            rag_context = "Here are some examples of previous successful job inquiries:\n\n"
            for i, msg in enumerate(similar_messages):
                rag_context += f"Example {i+1}: {msg['document']}\n\n"
        
        # Generate the message
        generated_message = linkedin_job_inquiry_request(
            name=contact_name,
            about_section=about_section,
            job_posting=job_posting,
            rag_context=rag_context
        )
        
        # Save to database
        inquiry = JobInquiry(
            job_application_id=job_application_id,
            contact_name=contact_name,
            contact_role=contact_role,
            date_reached_out=datetime.utcnow(),
            message_sent=generated_message
        )
        
        self.db.add(inquiry)
        self.db.commit()
        self.db.refresh(inquiry)
        
        # Add to vector store for future RAG
        self.inquiry_retriever.add_document(
            text=generated_message,
            metadata={
                "inquiry_id": inquiry.id,
                "job_application_id": job_application_id,
                "contact_name": contact_name,
                "contact_role": contact_role,
                "company": job_app.company,
                "job_title": job_app.job_title
            }
        )
        
        return {
            "id": inquiry.id,
            "job_application_id": job_application_id,
            "contact_name": contact_name,
            "contact_role": contact_role,
            "about_section": about_section,
            "job_posting": job_posting,
            "message_sent": generated_message
        }