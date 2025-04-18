import os
import openai
from dotenv import load_dotenv
from core.mcp.client import mcp_instance as mcp
from app.config import settings

# Create a global OpenAI Client with the API key from settings
client = openai.Client(api_key=settings.openai_api_key)

@mcp.tool()
def generate_linkedin_connection_request(name: str, about_section: str = "", rag_context: str = "") -> str:
    """
    Generates a short LinkedIn connection request (<300 characters)
    using the OpenAI API, enhanced with RAG for better personalization.
    """
    system_content = """
    You are an expert at writing short, personalized LinkedIn connection requests.
    Your task is to create a concise, friendly message that feels personal and tailored to the individual.
    """
    
    user_content = f"""
    Write a personalized LinkedIn connection request to {name}.

    About the person: {about_section}

    Requirements:
    - Must be under 300 characters total
    - Should feel warm and personal, not generic
    - Mention something specific about their background if available
    - Keep it concise yet engaging
    - No generic phrases like "I'd like to add you to my professional network"
    
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