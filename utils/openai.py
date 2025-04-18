import logging
import openai
from typing import List, Dict, Any, Optional

from app.config import settings

logger = logging.getLogger("openai_utils")

def get_openai_client():
    """
    Get a configured OpenAI client instance.
    """
    return openai.Client(api_key=settings.openai_api_key)

def handle_api_error(func):
    """
    Decorator for handling OpenAI API errors.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise ValueError(f"OpenAI API error: {str(e)}")
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit error: {str(e)}")
            raise ValueError("OpenAI rate limit exceeded. Please try again in a few minutes.")
        except Exception as e:
            logger.error(f"Error in OpenAI API call: {str(e)}")
            raise ValueError(f"Unexpected error: {str(e)}")
    return wrapper

@handle_api_error
def chat_completion(
    messages: List[Dict[str, str]], 
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> str:
    """
    Generate a chat completion using the OpenAI API.
    
    Args:
        messages: List of message objects (role, content)
        model: OpenAI model to use (defaults to settings.openai_model)
        temperature: Sampling temperature (0-2)
        max_tokens: Maximum number of tokens to generate
        
    Returns:
        The generated text
    """
    client = get_openai_client()
    
    response = client.chat.completions.create(
        model=model or settings.openai_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return response.choices[0].message.content