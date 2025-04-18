import os
import json
import openai
from core.mcp.client import mcp_instance as mcp
from app.config import settings
from typing import Dict, Any, Union, List

# Create a global OpenAI Client with the API key from settings
client = openai.Client(api_key=settings.openai_api_key)

@mcp.tool()
def generate_cover_letter_initial(
    resume_text: str, 
    job_description: str, 
    rag_context: str = ""
) -> Dict[str, Any]:
    """
    Given a resume and job description, decide whether there's sufficient context
    to generate a personalized cover letter. If sufficient, return the cover letter.
    If not, return follow-up questions as a JSON array.
    Enhanced with RAG for better personalization and relevance.
    """
    system_content = """
    You are an expert cover letter writer specializing in personalized, compelling cover letters.
    Your task is to either create a great cover letter or ask for more information if needed.
    """
    
    prompt = f"""
    Based on the resume and job description below, decide whether you have enough context to write a personalized cover letter.

    A great cover letter requires context about:
    - Why the applicant is interested in this specific company/role
    - The applicant's tone preference (e.g., professional, friendly, passionate)
    - Which specific projects or achievements to emphasize

    If sufficient context is provided, write a personalized cover letter (max 1 page) that includes the portfolio link: https://portfolio.example.com
    
    If any critical context is missing, respond with exactly: "FOLLOW-UP:" followed by a JSON array of 2-4 specific follow-up questions.
    Example: "FOLLOW-UP: ["What draws you to this company?", "Which project from your resume best demonstrates your skills for this role?"]"

    Resume:
    {resume_text}

    Job Description:
    {job_description}
    
    {rag_context}
    """
    
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    output = response.choices[0].message.content.strip()
    
    if output.startswith("FOLLOW-UP:"):
        try:
            questions_str = output[len("FOLLOW-UP:"):].strip()
            questions = json.loads(questions_str)
            return {"follow_up_needed": True, "questions": questions}
        except Exception:
            # Fallback questions in case of parsing error
            return {"follow_up_needed": True, "questions": [
                "What draws you to this company or role personally?",
                "Are there any projects from your resume you'd like to emphasize more?",
                "What tone do you prefer — professional, friendly, or passionate?",
                "Are there any achievements or skills you'd like highlighted more?"
            ]}
    else:
        return {"cover_letter": output, "follow_up_needed": False}

@mcp.tool()
def generate_cover_letter_final(
    resume_text: str, 
    job_description: str, 
    follow_up_answers: str, 
    rag_context: str = ""
) -> str:
    """
    Generates the final personalized cover letter using the resume, job description,
    and additional context provided in follow-up answers.
    Enhanced with RAG for better personalization and relevance.
    """
    system_content = """
    You are an expert cover letter writer specializing in personalized, compelling cover letters.
    Your task is to create a tailored cover letter that showcases the applicant's fit for the role.
    """
    
    prompt = f"""
    Write a personalized, engaging cover letter (max 1 page) using the following information:

    Resume:
    {resume_text}

    Job Description:
    {job_description}

    Additional Context (follow-up answers):
    {follow_up_answers}
    
    {rag_context}

    Requirements:
    - Highlight relevant skills, achievements, and projects from the resume
    - Align with the company's mission, values, and goals mentioned in the job description
    - Include the portfolio link: https://portfolio.example.com
    - Express the applicant's enthusiasm for the role based on the additional context
    - Use a tone that matches the applicant's preference
    - Maximum length of one page (approximately 3-4 paragraphs)
    - Include proper salutation and closing
    """
    
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    cover_letter = response.choices[0].message.content.strip()
    return cover_letter