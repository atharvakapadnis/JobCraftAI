from typing import Dict, List, Any, Optional
import openai
import json

from app.config import settings

# Initialize OpenAI client
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

class OpenAIService:
    @staticmethod
    async def generate_text(prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """
        Generate text using OpenAI's GPT model
        
        Args:
            prompt: The prompt to generate text from
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness (0.0-1.0)
            
        Returns:
            Generated text
        """
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Error generating text: {str(e)}")
    
    @staticmethod
    async def generate_structured_data(prompt: str, schema: Dict[str, Any], temperature: float = 0.3) -> Dict[str, Any]:
        """
        Generate structured data using OpenAI's GPT model
        
        Args:
            prompt: The prompt to generate structured data from
            schema: JSON schema defining the structure
            temperature: Controls randomness (0.0-1.0)
            
        Returns:
            Generated structured data as a dictionary
        """
        try:
            system_prompt = f"""
            You are an AI assistant that generates structured data based on input.
            Please generate valid data according to the following JSON schema:
            {json.dumps(schema, indent=2)}
            
            Your response should be ONLY valid JSON that follows this schema with no additional text.
            """
            
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            
            # Parse the response as JSON
            try:
                result = json.loads(response.choices[0].message.content.strip())
                return result
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                content = response.choices[0].message.content.strip()
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    return json.loads(json_str)
                raise Exception("Failed to parse structured data from response")
        except Exception as e:
            raise Exception(f"Error generating structured data: {str(e)}")
    
    @staticmethod
    async def parse_resume(resume_text: str) -> Dict[str, Any]:
        """
        Parse resume text into structured data
        
        Args:
            resume_text: The text content of the resume
            
        Returns:
            Structured resume data
        """
        schema = {
            "type": "object",
            "properties": {
                "contact_info": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"},
                        "location": {"type": "string"},
                        "linkedin": {"type": "string"},
                        "website": {"type": "string"}
                    }
                },
                "summary": {"type": "string"},
                "education": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "institution": {"type": "string"},
                            "degree": {"type": "string"},
                            "field_of_study": {"type": "string"},
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"},
                            "description": {"type": "string"}
                        }
                    }
                },
                "experience": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "company": {"type": "string"},
                            "title": {"type": "string"},
                            "location": {"type": "string"},
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"},
                            "description": {"type": "string"}
                        }
                    }
                },
                "skills": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "category": {"type": "string"}
                        }
                    }
                },
                "projects": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"},
                            "technologies": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }
            }
        }
        
        prompt = f"""
        Parse the following resume text into structured data:
        
        {resume_text}
        
        Extract all relevant information including contact information, summary, education history, 
        work experience, skills, and projects. If any section is missing from the resume, return an empty
        list or object for that section.
        """
        
        return await OpenAIService.generate_structured_data(prompt, schema)
    
    @staticmethod
    async def parse_job_description(job_description: str) -> Dict[str, Any]:
        """
        Parse job description into structured data
        
        Args:
            job_description: The text content of the job description
            
        Returns:
            Structured job data
        """
        schema = {
            "type": "object",
            "properties": {
                "required_skills": {"type": "array", "items": {"type": "string"}},
                "preferred_skills": {"type": "array", "items": {"type": "string"}},
                "required_experience": {"type": "string"},
                "required_education": {"type": "string"},
                "responsibilities": {"type": "array", "items": {"type": "string"}},
                "benefits": {"type": "array", "items": {"type": "string"}},
                "application_deadline": {"type": "string"}
            }
        }
        
        prompt = f"""
        Parse the following job description into structured data:
        
        {job_description}
        
        Extract all relevant information including required skills, preferred skills, required experience, 
        required education, responsibilities, benefits, and application deadline. If any section is missing 
        from the job description, return an empty list or null for that section.
        """
        
        return await OpenAIService.generate_structured_data(prompt, schema)
    
    @staticmethod
    async def generate_linkedin_message(
        name: str, 
        message_type: str, 
        about_section: Optional[str] = None,
        title: Optional[str] = None,
        company: Optional[str] = None,
        job_title: Optional[str] = None,
        company_name: Optional[str] = None,
        job_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a LinkedIn message based on the given parameters
        
        Args:
            name: Target person's name
            message_type: Type of message (connection_request or job_inquiry)
            about_section: Target person's About section
            title: Target person's title
            company: Target person's company
            job_title: Job title (for job inquiry)
            company_name: Company name (for job inquiry)
            job_description: Job description (for job inquiry)
            
        Returns:
            Dictionary with generated message and character count
        """
        prompt = ""
        
        if message_type == "connection_request":
            prompt = f"""
            Generate a personalized LinkedIn connection request to {name}.
            
            Additional information:
            """
            
            if title:
                prompt += f"Their title: {title}\n"
            if company:
                prompt += f"Their company: {company}\n"
            if about_section:
                prompt += f"Their About section: {about_section}\n"
                
            prompt += """
            Requirements:
            1. The message must be under 300 characters
            2. Make it personalized, professional, and engaging
            3. Reference their background, interests, or professional alignment
            4. Do not include generic phrases like "I came across your profile"
            5. Do not include any placeholders or variables
            
            Return only the message text with no additional explanation.
            """
        
        elif message_type == "job_inquiry":
            prompt = f"""
            Generate a personalized LinkedIn connection request to {name} for job inquiry.
            
            Additional information:
            """
            
            if title:
                prompt += f"Their title: {title}\n"
            if company:
                prompt += f"Their company: {company}\n"
            if about_section:
                prompt += f"Their About section: {about_section}\n"
            if job_title:
                prompt += f"Job title I'm interested in: {job_title}\n"
            if company_name:
                prompt += f"Company name: {company_name}\n"
            if job_description:
                prompt += f"Job description excerpt: {job_description[:200]}...\n"
                
            prompt += """
            Requirements:
            1. The message must be under 300 characters
            2. Mention their background or shared interests
            3. Express interest in the company and role
            4. Politely ask if they would be open to a brief conversation
            5. Make it personalized, professional, and engaging
            6. Do not include any placeholders or variables
            
            Return only the message text with no additional explanation.
            """
        
        # Generate the message
        message = await OpenAIService.generate_text(prompt, max_tokens=300, temperature=0.7)
        
        # Calculate character count
        character_count = len(message)
        
        return {
            "generated_message": message,
            "character_count": character_count
        }
    
    @staticmethod
    async def generate_resume_optimization(
        resume_data: Dict[str, Any],
        job_description: str
    ) -> Dict[str, Any]:
        """
        Generate resume optimization suggestions based on resume data and job description
        
        Args:
            resume_data: Structured resume data
            job_description: Job description text
            
        Returns:
            Dictionary with optimization suggestions and match score
        """
        schema = {
            "type": "object",
            "properties": {
                "match_score": {"type": "number"},
                "suggestions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "category": {"type": "string"},
                            "content": {"type": "string"},
                            "priority": {"type": "string"}
                        }
                    }
                },
                "skill_matches": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "skill_name": {"type": "string"},
                            "is_present": {"type": "string"},
                            "importance": {"type": "string"},
                            "suggestion": {"type": "string"}
                        }
                    }
                }
            }
        }
        
        prompt = f"""
        Analyze the resume and job description to provide optimization suggestions:
        
        Resume data:
        {json.dumps(resume_data, indent=2)}
        
        Job description:
        {job_description}
        
        Generate the following:
        1. A match score between 0 and 1 representing how well the resume matches the job description
        2. Specific suggestions to improve the resume for this job
        3. Analysis of skill matches between the resume and job requirements
        
        Your suggestions should focus on:
        - Adding relevant keywords to increase ATS compatibility
        - Highlighting relevant experience and projects
        - Reformatting or rewording sections to better align with the job
        - DO NOT suggest fabricating or inventing experience, skills, or qualifications
        """
        
        return await OpenAIService.generate_structured_data(prompt, schema)
    
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
            tone: Tone of the cover letter
            emphasized_projects: List of projects to emphasize
            emphasized_skills: List of skills to emphasize
            emphasized_experiences: List of experiences to emphasize
            personal_note: Additional context from the user
            portfolio_url: User's portfolio URL
            
        Returns:
            Generated cover letter text
        """
        # Prepare prompt
        prompt = f"""
        Generate a personalized cover letter based on the following information:
        
        Resume data:
        {json.dumps(resume_data, indent=2)}
        
        Job description:
        {job_description}
        
        Company name: {company_name}
        Job title: {job_title}
        Tone: {tone}
        """
        
        if emphasized_projects:
            prompt += f"\nProjects to emphasize: {', '.join(emphasized_projects)}"
        
        if emphasized_skills:
            prompt += f"\nSkills to emphasize: {', '.join(emphasized_skills)}"
        
        if emphasized_experiences:
            prompt += f"\nExperiences to emphasize: {', '.join(emphasized_experiences)}"
        
        if personal_note:
            prompt += f"\nAdditional context from the user: {personal_note}"
        
        if portfolio_url:
            prompt += f"\nPortfolio URL to include: {portfolio_url}"
        
        prompt += """
        Guidelines:
        1. Create a professional and personalized cover letter
        2. Highlight relevant skills and experiences that match the job description
        3. Explain why the candidate is interested in the position and company
        4. Include a call to action in the closing paragraph
        5. Keep the letter concise (about 300-400 words)
        6. Use a tone that matches the specified preference
        7. Format the letter properly with appropriate greeting and closing
        8. Include the portfolio URL if provided
        
        Return only the cover letter text with no additional explanation.
        """
        
        return await OpenAIService.generate_text(prompt, max_tokens=1000, temperature=0.7)