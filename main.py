import uvicorn
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("main")

def run_app():
    """Run the FastAPI application."""
    logger.info("Starting JobCraftAI application")
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )

if __name__ == "__main__":
    run_app()