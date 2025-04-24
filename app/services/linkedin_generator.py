from typing import Dict, Any, Optional
from app.services.openai_service import OpenAIService

class LinkedInGenerator:
    """
    Service for generating LinkedIn messages
    """
    
    @staticmethod
    async def generate_connection_request(
        name: str,
        about_section: Optional[str] = None,
        title: Optional[str] = None,
        company: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a LinkedIn connection request message
        
        Args:
            name: Target person's name
            about_section: Target person's About section
            title: Target person's title
            company: Target person's company
            
        Returns:
            Dictionary with generated message and character count
        """
        return await OpenAIService.generate_linkedin_message(
            name=name,
            message_type="connection_request",
            about_section=about_section,
            title=title,
            company=company
        )
    
    @staticmethod
    async def generate_job_inquiry(
        name: str,
        job_title: str,
        company_name: str,
        about_section: Optional[str] = None,
        title: Optional[str] = None,
        company: Optional[str] = None,
        job_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a LinkedIn job inquiry message
        
        Args:
            name: Target person's name
            job_title: Job title
            company_name: Company name
            about_section: Target person's About section
            title: Target person's title
            company: Target person's company
            job_description: Job description
            
        Returns:
            Dictionary with generated message and character count
        """
        return await OpenAIService.generate_linkedin_message(
            name=name,
            message_type="job_inquiry",
            about_section=about_section,
            title=title,
            company=company,
            job_title=job_title,
            company_name=company_name,
            job_description=job_description
        )