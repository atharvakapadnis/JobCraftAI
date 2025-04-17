# JobCraftAI

An intelligent job application assistant that helps with LinkedIn connection requests, resume optimization, and cover letter generation using AI.

## Features

- Create personalized LinkedIn connection requests
- Generate targeted LinkedIn job inquiry messages
- Optimize resumes for specific job descriptions
- Create tailored cover letters
- RAG (Retrieval-Augmented Generation) for more relevant outputs
- Modular, well-structured codebase

## Installation

1. Clone this repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with your API keys (see `.env.example`)
6. Run the application: `uvicorn app.main:app --reload`

## API Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run tests with pytest: