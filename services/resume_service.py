from sqlalchemy.orm import Session
from typing import Dict, Any

from models.models import JobApplication, ResumeSuggestion
from tools.resume_optimization import resume_optimization
from core.rag.retrieval import DocumentRetriever

class ResumeService:
    def __init__(self, db: Session):
        self.db = db
        self.retriever = DocumentRetriever("resume_suggestions")
        
    def optimize_resume(
        self,
        resume_text: str,
        job_application_id: int,
        job_description: str
    ) -> Dict[str, Any]:
        """
        Generate optimization suggestions for a resume based on a job description.
        """
        # Check if the job application exists
        job_app = self.db.query(JobApplication).filter(JobApplication.id == job_application_id).first()
        if not job_app:
            raise ValueError(f"Job application with ID {job_application_id} not found")
            
        # Get similar previous suggestions for RAG context
        similar_suggestions = self.retriever.retrieve(
            query=f"{job_app.job_title} {job_app.company} {job_description}",
            k=3
        )
        
        # Prepare RAG context
        rag_context = ""
        if similar_suggestions:
            rag_context = "Here are some examples of previous successful resume optimizations for similar roles:\n\n"
            for i, sugg in enumerate(similar_suggestions):
                rag_context += f"Example {i+1}: {sugg['document']}\n\n"
        
        # Generate the suggestions
        suggestions = resume_optimization(
            resume_text=resume_text,
            job_description=job_description,
            rag_context=rag_context
        )
        
        # Save to database
        resume_suggestion = ResumeSuggestion(
            job_application_id=job_application_id,
            suggestions=suggestions,
            resume_text=resume_text
        )
        
        self.db.add(resume_suggestion)
        self.db.commit()
        self.db.refresh(resume_suggestion)
        
        # Add to vector store for future RAG
        self.retriever.add_document(
            text=suggestions,
            metadata={
                "suggestion_id": resume_suggestion.id,
                "job_application_id": job_application_id,
                "job_title": job_app.job_title,
                "company": job_app.company
            }
        )
        
        return {
            "suggestions": suggestions,
            "job_application_id": job_application_id,
            "resume_suggestion_id": resume_suggestion.id
        }