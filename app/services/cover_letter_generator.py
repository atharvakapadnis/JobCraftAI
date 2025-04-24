from typing import Dict, Any, Optional, List
from app.services.openai_service import OpenAIService

class CoverLetterGenerator:
    """
    Service for generating cover letters
    """
    
    @staticmethod
    async def generate_cover_letter(
        resume_data: Dict[str, Any],
        job_description: str,
        company_name: str,
        job_title: str,
        tone: str = "professional",
        emphasized_projects: Optional[List[str]] = None,
        emphasized_skills: Optional[List[str]] = None,
        emphasized_experiences: Optional[List[str]] = None,
        personal_note: Optional[str] = None,
        portfolio_url: Optional[str] = None
    ) -> str:
        """
        Generate a cover letter based on resume data and job description
        
        Args:
            resume_data: Structured resume data
            job_description: Job description text
            company_name: Company name
            job_title: Job title
            tone: Tone of the cover letter (formal, friendly, enthusiastic, etc.)
            emphasized_projects: List of projects to emphasize
            emphasized_skills: List of skills to emphasize
            emphasized_experiences: List of experiences to emphasize
            personal_note: Additional context from the user
            portfolio_url: User's portfolio URL
            
        Returns:
            Generated cover letter text
        """
        return await OpenAIService.generate_cover_letter(
            resume_data=resume_data,
            job_description=job_description,
            company_name=company_name,
            job_title=job_title,
            tone=tone,
            emphasized_projects=emphasized_projects,
            emphasized_skills=emphasized_skills,
            emphasized_experiences=emphasized_experiences,
            personal_note=personal_note,
            portfolio_url=portfolio_url
        )