import pytest
from unittest.mock import patch

from tools.linkedin_connection import generate_linkedin_connection_request
from tools.job_inquiry import linkedin_job_inquiry_request
from tools.resume_optimization import resume_optimization
from tools.cover_letter import generate_cover_letter_initial, generate_cover_letter_final

class TestLinkedInTools:
    @patch("openai.Client")
    def test_generate_linkedin_connection_request(self, mock_client):
        # Mock the OpenAI API response
        mock_completion = type('obj', (object,), {
            'choices': [
                type('obj', (object,), {
                    'message': type('obj', (object,), {
                        'content': "Hi Jane, I came across your profile and was impressed by your work in AI ethics. Let's connect!"
                    })
                })
            ]
        })
        mock_client.return_value.chat.completions.create.return_value = mock_completion
        
        result = generate_linkedin_connection_request(
            name="Jane Smith",
            about_section="Expert in AI ethics",
            rag_context=""
        )
        
        assert len(result) <= 300
        assert "Jane" in result
        assert "AI ethics" in result
        
    @patch("openai.Client")
    def test_linkedin_job_inquiry_request(self, mock_client):
        # Mock the OpenAI API response
        mock_completion = type('obj', (object,), {
            'choices': [
                type('obj', (object,), {
                    'message': type('obj', (object,), {
                        'content': "Hi John, I recently applied for the developer role at your company. Would love to chat about the team culture."
                    })
                })
            ]
        })
        mock_client.return_value.chat.completions.create.return_value = mock_completion
        
        result = linkedin_job_inquiry_request(
            name="John Doe",
            about_section="Engineering Manager",
            job_posting="Software Developer position",
            rag_context=""
        )
        
        assert len(result) <= 300
        assert "John" in result
        assert "applied" in result.lower()

class TestResumeTools:
    @patch("openai.Client")
    def test_resume_optimization(self, mock_client, sample_resume_text, sample_job_description):
        # Mock the OpenAI API response
        mock_completion = type('obj', (object,), {
            'choices': [
                type('obj', (object,), {
                    'message': type('obj', (object,), {
                        'content': "1. Highlight your Python experience\n2. Add more details about CI/CD"
                    })
                })
            ]
        })
        mock_client.return_value.chat.completions.create.return_value = mock_completion
        
        result = resume_optimization(
            resume_text=sample_resume_text,
            job_description=sample_job_description,
            rag_context=""
        )
        
        assert "Python" in result
        assert "CI/CD" in result

class TestCoverLetterTools:
    @patch("openai.Client")
    def test_generate_cover_letter_initial_with_follow_up(self, mock_client, sample_resume_text, sample_job_description):
        # Mock the OpenAI API response for follow-up case
        mock_completion = type('obj', (object,), {
            'choices': [
                type('obj', (object,), {
                    'message': type('obj', (object,), {
                        'content': 'FOLLOW-UP: ["What draws you to this company?", "Which projects are you most proud of?"]'
                    })
                })
            ]
        })
        mock_client.return_value.chat.completions.create.return_value = mock_completion
        
        result = generate_cover_letter_initial(
            resume_text=sample_resume_text,
            job_description=sample_job_description,
            rag_context=""
        )
        
        assert result["follow_up_needed"] == True
        assert len(result["questions"]) == 2
        assert "company" in result["questions"][0].lower()
        
    @patch("openai.Client")
    def test_generate_cover_letter_initial_with_letter(self, mock_client, sample_resume_text, sample_job_description):
        # Mock the OpenAI API response for cover letter case
        mock_completion = type('obj', (object,), {
            'choices': [
                type('obj', (object,), {
                    'message': type('obj', (object,), {
                        'content': "Dear Hiring Manager,\n\nI am excited to apply for the Senior Software Developer position at your company..."
                    })
                })
            ]
        })
        mock_client.return_value.chat.completions.create.return_value = mock_completion
        
        result = generate_cover_letter_initial(
            resume_text=sample_resume_text,
            job_description=sample_job_description,
            rag_context=""
        )
        
        assert result.get("follow_up_needed", False) == False
        assert "cover_letter" in result
        assert result["cover_letter"].startswith("Dear Hiring Manager")
        
    @patch("openai.Client")
    def test_generate_cover_letter_final(self, mock_client, sample_resume_text, sample_job_description):
        # Mock the OpenAI API response
        mock_completion = type('obj', (object,), {
            'choices': [
                type('obj', (object,), {
                    'message': type('obj', (object,), {
                        'content': "Dear Hiring Manager,\n\nWith great enthusiasm, I submit my application for the Senior Software Developer position..."
                    })
                })
            ]
        })
        mock_client.return_value.chat.completions.create.return_value = mock_completion
        
        result = generate_cover_letter_final(
            resume_text=sample_resume_text,
            job_description=sample_job_description,
            follow_up_answers="I'm drawn to your company's focus on innovation. My CI/CD project was my most significant achievement.",
            rag_context=""
        )
        
        assert result.startswith("Dear Hiring Manager")
        assert "submit my application" in result