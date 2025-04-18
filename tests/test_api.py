import pytest
import io
from fastapi.testclient import TestClient

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_job_application(client):
    data = {
        "company": "Test Company",
        "job_title": "Test Job",
        "job_description": "This is a test job description."
    }
    
    response = client.post("/api/job-applications/", json=data)
    assert response.status_code == 201
    result = response.json()
    
    assert result["company"] == data["company"]
    assert result["job_title"] == data["job_title"]
    assert result["job_description"] == data["job_description"]
    assert "id" in result
    assert "date_applied" in result

def test_get_job_applications(client, sample_job_application):
    response = client.get("/api/job-applications/")
    assert response.status_code == 200
    result = response.json()
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert result[0]["company"] == sample_job_application.company
    assert result[0]["job_title"] == sample_job_application.job_title

def test_get_job_application(client, sample_job_application):
    response = client.get(f"/api/job-applications/{sample_job_application.id}")
    assert response.status_code == 200
    result = response.json()
    
    assert result["id"] == sample_job_application.id
    assert result["company"] == sample_job_application.company
    assert result["job_title"] == sample_job_application.job_title

def test_create_linkedin_request(client, monkeypatch):
    # Mock the generate_linkedin_connection_request function
    def mock_generate(name, about_section, rag_context=""):
        return f"Mock connection request for {name}"
    
    from tools import linkedin_connection
    monkeypatch.setattr(
        linkedin_connection, 
        "generate_linkedin_connection_request",
        mock_generate
    )
    
    data = {
        "name": "Test Person",
        "role": "Test Role",
        "company": "Test Company",
        "about_section": "Test About Section"
    }
    
    response = client.post("/api/linkedin/connection-request", json=data)
    assert response.status_code == 201
    result = response.json()
    
    assert result["name"] == data["name"]
    assert result["role"] == data["role"]
    assert result["message_sent"] == "Mock connection request for Test Person"

def test_create_job_inquiry(client, sample_job_application, monkeypatch):
    # Mock the linkedin_job_inquiry_request function
    def mock_inquiry(name, about_section="", job_posting="", rag_context=""):
        return f"Mock job inquiry for {name} about {job_posting[:10]}..."
    
    from tools import job_inquiry
    monkeypatch.setattr(
        job_inquiry,
        "linkedin_job_inquiry_request",
        mock_inquiry
    )
    
    data = {
        "job_application_id": sample_job_application.id,
        "contact_name": "Test Contact",
        "contact_role": "Hiring Manager",
        "about_section": "Test About Section",
        "job_posting": "Test Job Posting"
    }
    
    response = client.post("/api/linkedin/job-inquiry", json=data)
    assert response.status_code == 201
    result = response.json()
    
    assert result["contact_name"] == data["contact_name"]
    assert result["contact_role"] == data["contact_role"]
    assert result["job_application_id"] == sample_job_application.id
    assert "message_sent" in result