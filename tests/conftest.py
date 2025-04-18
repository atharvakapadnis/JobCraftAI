import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.dependencies import get_db
from app.database import Base
from models.models import JobApplication, Person, JobInquiry, ResumeSuggestion, CoverLetter

# Create test database
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def test_db():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session for the test
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
    # Drop the tables after the test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    # Override the get_db dependency to use the test database
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
            
    app.dependency_overrides[get_db] = override_get_db
    
    # Create a test client
    with TestClient(app) as client:
        yield client
        
    # Remove the override after the test
    app.dependency_overrides.clear()

@pytest.fixture
def sample_job_application(test_db):
    # Create a sample job application
    job_app = JobApplication(
        company="Test Company",
        job_title="Test Job",
        job_description="This is a test job description."
    )
    test_db.add(job_app)
    test_db.commit()
    test_db.refresh(job_app)
    
    return job_app

@pytest.fixture
def sample_resume_text():
    return """
    John Doe
    Software Developer
    123 Main St, Anytown, USA
    email@example.com | (555) 123-4567 | linkedin.com/in/johndoe
    
    EXPERIENCE
    Senior Software Developer | Tech Solutions Inc. | 2018-Present
    - Developed RESTful APIs using Python and Flask
    - Implemented CI/CD pipelines using Jenkins
    - Led a team of 5 developers on a major product release
    
    Software Developer | Code Masters | 2015-2018
    - Built web applications using JavaScript and React
    - Designed and implemented database schemas using PostgreSQL
    - Collaborated with cross-functional teams to deliver projects on time
    
    EDUCATION
    Bachelor of Science in Computer Science | University of Technology | 2015
    
    SKILLS
    Languages: Python, JavaScript, SQL
    Frameworks: Flask, React, Django
    Tools: Git, Docker, AWS
    """

@pytest.fixture
def sample_job_description():
    return """
    We are looking for a Senior Software Developer with expertise in Python and web development.
    The ideal candidate has experience with RESTful APIs, CI/CD pipelines, and team leadership.
    
    Responsibilities:
    - Design and develop high-quality web applications
    - Implement and maintain CI/CD pipelines
    - Mentor junior developers
    - Collaborate with product managers to define requirements
    
    Requirements:
    - 5+ years of experience in software development
    - Strong knowledge of Python, JavaScript, and SQL
    - Experience with web frameworks like Flask or Django
    - Familiarity with containerization technologies
    - Excellent communication and leadership skills
    """