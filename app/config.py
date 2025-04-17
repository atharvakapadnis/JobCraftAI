import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    app_name: str = "JobCraftAI"
    description: str = "AI-powered job application assistant"
    version: str = "1.0.0"
    
    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./jobcraftai.db")
    
    # OpenAI API settings
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    # RAG settings
    vector_db_path: str = "./vector_db"
    
    # CORS settings
    allowed_origins: list = ["*"]
    
    # Rate limiting
    rate_limit: int = 100  # requests per minute
    
    class Config:
        env_file = ".env"

settings = Settings()