from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import json

from models.models import JobApplication, CoverLetter
from tools.cover_letter import generate_cover_letter_initial, generate_cover_letter_final
from core.rag.retrieval import DocumentRetriever

class CoverLetterService:
    def __init__(self, db: Session):
        self.db = db
        self.retriever = DocumentRetriever("cover_letters")
        
    def generate_cover_letter(
        self,
        resume_text: str,
        job_application_id: int,
        job_description: str,
        follow_up_answers: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a cover letter based on resume and job description.
        If insufficient context, will return follow-up questions.
        """
        # Check if the job application exists
        job_app = self.db.query(JobApplication).filter(JobApplication.id == job_application_id).first()
        if not job_app:
            raise ValueError(f"Job application with ID {job_application_id} not found")
            
        # Get similar previous cover letters for RAG context
        similar_letters = self.retriever.retrieve(
            query=f"{job_app.job_title} {job_app.company} {job_description}",
            k=2
        )
        
        # Prepare RAG context
        rag_context = ""
        if similar_letters:
            rag_context = "Here are some examples of previous successful cover letters for similar roles:\n\n"
            for i, letter in enumerate(similar_letters):
                rag_context += f"Example {i+1}: {letter['document']}\n\n"
        
        # Generate the initial cover letter or follow-up questions
        if not follow_up_answers:
            result = generate_cover_letter_initial(
                resume_text=resume_text,
                job_description=job_description,
                rag_context=rag_context
            )
            
            if result.get("follow_up_needed"):
                return {
                    "follow_up_needed": True,
                    "questions": result.get("questions", [])
                }
            else:
                cover_letter_text = result.get("cover_letter")
        else:
            # If follow-up answers were provided, generate the final cover letter
            cover_letter_text = generate_cover_letter_final(
                resume_text=resume_text,
                job_description=job_description,
                follow_up_answers=follow_up_answers,
                rag_context=rag_context
            )
        
        # Save to database
        cover_letter = CoverLetter(
            job_application_id=job_application_id,
            cover_letter=cover_letter_text,
            follow_up_answers=follow_up_answers
        )
        
        self.db.add(cover_letter)
        self.db.commit()
        self.db.refresh(cover_letter)
        
        # Add to vector store for future RAG
        self.retriever.add_document(
            text=cover_letter_text,
            metadata={
                "cover_letter_id": cover_letter.id,
                "job_application_id": job_application_id,
                "job_title": job_app.job_title,
                "company": job_app.company
            }
        )
        
        return {
            "cover_letter": cover_letter_text,
            "job_application_id": job_application_id,
            "cover_letter_id": cover_letter.id,
            "length": len(cover_letter_text)
        }