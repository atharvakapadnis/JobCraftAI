import pytest
from datetime import datetime

from models.models import JobApplication, Person, JobInquiry, ResumeSuggestion, CoverLetter

def test_create_person(test_db):
    person = Person(
        contact_name="Test Person",
        contact_role="Test Role",
        contact_company="Test Company",
        message_sent="Test message"
    )
    
    test_db.add(person)
    test_db.commit()
    test_db.refresh(person)
    
    assert person.id is not None
    assert person.contact_name == "Test Person"
    assert person.contact_role == "Test Role"
    assert person.contact_company == "Test Company"
    assert person.message_sent == "Test message"
    assert person.created_at is not None

def test_create_job_application(test_db):
    job_app = JobApplication(
        company="Test Company",
        job_title="Test Job",
        job_description="Test description",
        date_applied=datetime.utcnow()
    )
    
    test_db.add(job_app)
    test_db.commit()
    test_db.refresh(job_app)
    
    assert job_app.id is not None
    assert job_app.company == "Test Company"
    assert job_app.job_title == "Test Job"
    assert job_app.job_description == "Test description"
    assert job_app.date_applied is not None
    assert job_app.resume_suggestion is None
    assert job_app.cover_letter is None
    assert len(job_app.job_inquiries) == 0

def test_relationships(test_db):
    # Create job application
    job_app = JobApplication(
        company="Test Company",
        job_title="Test Job",
        job_description="Test description"
    )
    test_db.add(job_app)
    test_db.commit()
    test_db.refresh(job_app)
    
    # Create resume suggestion
    resume_suggestion = ResumeSuggestion(
        job_application_id=job_app.id,
        suggestions="Test suggestions",
        resume_text="Test resume text"
    )
    test_db.add(resume_suggestion)
    
    # Create cover letter
    cover_letter = CoverLetter(
        job_application_id=job_app.id,
        cover_letter="Test cover letter",
        follow_up_answers="Test follow-up answers"
    )
    test_db.add(cover_letter)
    
    # Create job inquiry
    job_inquiry = JobInquiry(
        job_application_id=job_app.id,
        contact_name="Test Contact",
        contact_role="Test Role",
        message_sent="Test message"
    )
    test_db.add(job_inquiry)
    
    test_db.commit()
    
    # Refresh job application to load relationships
    test_db.refresh(job_app)
    
    # Check relationships
    assert job_app.resume_suggestion is not None
    assert job_app.resume_suggestion.suggestions == "Test suggestions"
    
    assert job_app.cover_letter is not None
    assert job_app.cover_letter.cover_letter == "Test cover letter"
    
    assert len(job_app.job_inquiries) == 1
    assert job_app.job_inquiries[0].contact_name == "Test Contact"
    
    # Check relationships from the other direction
    assert resume_suggestion.job_application.id == job_app.id
    assert cover_letter.job_application.id == job_app.id
    assert job_inquiry.job_application.id == job_app.id