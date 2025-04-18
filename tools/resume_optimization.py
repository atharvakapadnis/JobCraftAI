import os
import openai
from core.mcp.client import mcp_instance as mcp
from app.config import settings

# Create a global OpenAI Client with the API key from settings
client = openai.Client(api_key=settings.openai_api_key)

@mcp.tool()
def resume_optimization(
    resume_text: str, 
    job_description: str, 
    rag_context: str = ""
) -> str:
    """
    Generates resume optimization suggestions based on the provided resume text and job description.
    Enhanced with RAG for better personalization and relevance.
    
    The suggestions should:
      - Identify relevant keywords, phrases, and requirements from the job description.
      - Recommend natural ways to incorporate these into the existing resume.
      - Suggest rewording, emphasizing, or reordering existing projects, experiences, or skills.
      - Avoid fabricating any new information.
    """
    system_content = """
    You are an expert in resume optimization and improving ATS compatibility.
    Your task is to help job seekers tailor their resumes to specific job descriptions.
    """
    
    prompt = f"""
    Provide clear, concise, and impactful suggestions to improve the resume below for the given job description.
    
    Focus on:
    - Identifying key keywords, phrases, and requirements from the job description.
    - Recommending how to naturally incorporate these into the existing resume.
    - Suggesting where existing projects, experiences, or skills can be reworded, emphasized, or reordered.
    - Highlighting format or structure improvements for better ATS compatibility.
    
    Do not invent any new experiences, skills, or projects.
    Format your suggestions in clear, actionable bullet points.

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
        temperature=0.7,
    )
    
    suggestions = response.choices[0].message.content.strip()
    return suggestions