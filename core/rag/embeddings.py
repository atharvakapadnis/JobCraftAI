import os
import openai
from app.config import settings
from typing import List, Dict, Any

# Configure OpenAI client
openai.api_key = settings.openai_api_key

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Get embeddings for a list of texts using OpenAI's API.
    
    Args:
        texts: List of texts to embed
        
    Returns:
        List of embedding vectors
    """
    if not texts:
        return []
        
    response = openai.embeddings.create(
        model=settings.embedding_model,
        input=texts,
    )
    
    # Extract embeddings from response
    embeddings = [item.embedding for item in response.data]
    
    return embeddings

def get_single_embedding(text: str) -> List[float]:
    """
    Get embedding for a single text.
    
    Args:
        text: Text to embed
        
    Returns:
        Embedding vector
    """
    embeddings = get_embeddings([text])
    return embeddings[0] if embeddings else []