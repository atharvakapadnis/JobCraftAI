from typing import Dict, Any
from app.services.openai_service import OpenAIService

class ResumeOptimizer:
    """
    Service for optimizing resumes for specific job applications
    """
    
    @staticmethod
    async def optimize_resume(
        resume_data: Dict[str, Any],
        job_description: str
    ) -> Dict[str, Any]:
        """
        Generate optimization suggestions for a resume based on a job description
        
        Args:
            resume_data: Structured resume data
            job_description: Job description text
            
        Returns:
            Dictionary with optimization suggestions, match score, and skill matches
        """
        return await OpenAIService.generate_resume_optimization(
            resume_data=resume_data,
            job_description=job_description
        )