# JobCraftAI

JobCraftAI is an AI-powered job application assistant that helps job seekers optimize their applications with personalized content generation.

## Features

### Core Features
- **Resume Parsing**: Upload and parse your resume into structured data
- **LinkedIn Message Generation**: Create personalized connection requests and job inquiries
- **Resume Optimization**: Get tailored suggestions to improve your resume for specific jobs
- **Cover Letter Generation**: Generate customized cover letters based on your resume and job descriptions
- **Job Application Tracking**: Keep track of all your job applications in one place

## Tech Stack

- **Backend**: FastAPI
- **Database**: SQLAlchemy with SQLite/PostgreSQL
- **AI Integration**: OpenAI API (GPT-4o-mini)
- **Integration Protocol**: Model Context Protocol (MCP)

## Installation

### Prerequisites
- Python 3.9+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/jobcraftai.git
cd jobcraftai
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on the `.env.example` template:
```bash
cp .env.example .env
```

5. Edit the `.env` file to add your OpenAI API key and other settings.

6. Initialize the database:
```bash
# First time setup (if using Alembic)
alembic upgrade head

# Alternatively, the application will create the database automatically on first run
```

7. Run the application:
```bash
uvicorn app.main:app --reload
```

8. Access the API at `http://localhost:8000` and the documentation at `http://localhost:8000/docs`

## Usage

### API Endpoints

#### Authentication
- `POST /api/auth/token` - Get an access token (OAuth2)
- `POST /api/auth/login` - Login with email and password

#### Users
- `POST /api/users` - Create a new user
- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update current user profile

#### Resumes
- `POST /api/resumes` - Upload a new resume
- `GET /api/resumes` - Get all user resumes
- `GET /api/resumes/{resume_id}` - Get a specific resume
- `GET /api/resumes/{resume_id}/parsed` - Get parsed content of a resume
- `DELETE /api/resumes/{resume_id}` - Delete a resume

#### Job Applications
- `POST /api/job-applications` - Create a new job application
- `GET /api/job-applications` - Get all job applications
- `GET /api/job-applications/{job_application_id}` - Get a specific job application
- `PUT /api/job-applications/{job_application_id}` - Update a job application
- `DELETE /api/job-applications/{job_application_id}` - Delete a job application
- `GET /api/job-applications/{job_application_id}/parsed` - Get parsed job details

#### LinkedIn Messages
- `POST /api/linkedin` - Create a new LinkedIn message
- `GET /api/linkedin` - Get all LinkedIn messages
- `GET /api/linkedin/{linkedin_message_id}` - Get a specific LinkedIn message
- `PUT /api/linkedin/{linkedin_message_id}` - Update a LinkedIn message
- `DELETE /api/linkedin/{linkedin_message_id}` - Delete a LinkedIn message
- `POST /api/linkedin/generate` - Generate a LinkedIn message without saving
- `PUT /api/linkedin/{linkedin_message_id}/mark-sent` - Mark a message as sent

#### Cover Letters
- `POST /api/cover-letters` - Create a new cover letter
- `GET /api/cover-letters` - Get all cover letters
- `GET /api/cover-letters/{cover_letter_id}` - Get a specific cover letter
- `PUT /api/cover-letters/{cover_letter_id}` - Update a cover letter
- `DELETE /api/cover-letters/{cover_letter_id}` - Delete a cover letter
- `POST /api/cover-letters/generate` - Generate a cover letter without saving

#### Resume Optimizations
- `POST /api/resume-optimizations` - Create a new resume optimization
- `GET /api/resume-optimizations` - Get all resume optimizations
- `GET /api/resume-optimizations/{optimization_id}` - Get a specific resume optimization
- `DELETE /api/resume-optimizations/{optimization_id}` - Delete a resume optimization
- `POST /api/resume-optimizations/optimize` - Generate optimization suggestions without saving

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [OpenAI](https://openai.com/) for providing the AI models
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) for the ORM
- [Anthropic](https://www.anthropic.com/) for the Model Context Protocol (MCP)