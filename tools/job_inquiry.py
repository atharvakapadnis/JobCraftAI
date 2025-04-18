import os
import openai
from core.mcp.client import mcp_instance as mcp
from app.config import settings

# Create a global OpenAI Client with the API key from settings
client = openai.Client(api_key=settings.openai_api_key)

@mcp.tool()
def linkedin_job_inquiry_request(
    name: str, 
    about_section: str = "", 
    job_posting: str = "",
    rag_context: str = ""
) -> str:
    """
    Generates a short LinkedIn job inquiry request (<300 characters).
    Incorporates the person's name, optional About section, and the job posting.
    Emphasizes that the user has already applied for the role.
    Enhanced with RAG for better personalization and relevance.
    """
    system_content = """
    You are an expert at writing personalized, effective LinkedIn job inquiry messages.
    Your task is to help job seekers connect with people at companies where they've applied.
    """

    user_content = f"""
    Write a short LinkedIn connection request to {name} regarding a job application.

    About {name}: {about_section}

    Job posting details: {job_posting}

    Requirements:
    - Must be under 300 characters total (this is LinkedIn's limit)
    - Mention that I have already applied for a role at their company
    - Reference their background if relevant information is available
    - Politely ask if they'd be open to a brief conversation about the role or company
    - Must be warm and professional, not generic or overly formal
    
    {rag_context}
    """

    # Call the Chat Completions endpoint
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ],
        temperature=0.7,
        max_tokens=150
    )

    # Extract the generated text
    message = response.choices[0].message.content.strip()

    # Enforce 300-character limit
    if len(message) > 300:
        message = message[:300].rstrip()
        # Try to end at a sentence or punctuation if possible
        for i in range(len(message)-1, max(0, len(message)-20), -1):
            if message[i] in ['.', '!', '?']:
                message = message[:i+1]
                break

    return message