import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from core.mcp.client import mcp_instance
from core.mcp.fastapi_integration import register_mcp_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("app")

# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database and other resources
    logger.info("Initializing application...")
    init_db()
    logger.info("Database initialized")
    
    # Initialize RAG components if needed
    # initialize_rag()
    
    yield
    
    # Shutdown: Clean up resources
    logger.info("Application shutting down")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.version,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register MCP tools with FastAPI
register_mcp_tools(app, mcp_instance, prefix="/tools")

# Import and include routers
from api.endpoints import job_applications, linkedin, resume, cover_letter

app.include_router(job_applications.router, prefix="/api/job-applications", tags=["job-applications"])
app.include_router(linkedin.router, prefix="/api/linkedin", tags=["linkedin"])
app.include_router(resume.router, prefix="/api/resume", tags=["resume"])
app.include_router(cover_letter.router, prefix="/api/cover-letter", tags=["cover-letter"])

# Root endpoint
@app.get("/")
def root():
    return {
        "app_name": settings.app_name,
        "description": settings.description,
        "version": settings.version,
        "docs_url": "/docs",
    }

# Health check endpoint
@app.get("/health", tags=["health"])
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)