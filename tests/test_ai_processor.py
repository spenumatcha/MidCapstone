import pytest
from unittest.mock import Mock, patch
from backend.main import AIProcessor
import json

@pytest.fixture
def mock_groq_client():
    with patch('groq.Client') as mock_client:
        # Create a mock response object
        mock_response = Mock()
        mock_response.choices = [
            Mock(
                message=Mock(
                    content=json.dumps({
                        "full_name": "John Doe",
                        "email": "john@example.com",
                        "phone": "123-456-7890",
                        "location": "New York, NY",
                        "summary": "Experienced software engineer",
                        "experience": [
                            {
                                "company": "Tech Corp",
                                "title": "Senior Engineer",
                                "dates": "2020-2023",
                                "responsibilities": ["Led team of 5 developers"]
                            }
                        ],
                        "education": ["BS Computer Science, University of Tech"],
                        "skills": ["Python", "JavaScript", "AWS"],
                        "certifications": ["AWS Certified Developer"],
                        "projects": ["Built AI-powered resume parser"]
                    })
                )
            )
        ]
        
        # Configure the mock client
        mock_instance = mock_client.return_value
        mock_instance.chat.completions.create.return_value = mock_response
        yield mock_instance

@pytest.fixture
def ai_processor(mock_groq_client):
    with patch.dict('os.environ', {'GROQ_API_KEY': 'test_key'}):
        processor = AIProcessor()
        yield processor

def test_extract_resume_data(ai_processor, mock_groq_client):
    # Test data
    resume_text = """
    John Doe
    john@example.com
    123-456-7890
    New York, NY
    
    EXPERIENCE
    Tech Corp - Senior Engineer (2020-2023)
    - Led team of 5 developers
    
    EDUCATION
    BS Computer Science, University of Tech
    
    SKILLS
    Python, JavaScript, AWS
    
    CERTIFICATIONS
    AWS Certified Developer
    
    PROJECTS
    Built AI-powered resume parser
    """
    
    # Call the method
    result = ai_processor.extract_resume_data(resume_text)
    
    # Verify the result
    assert isinstance(result, dict)
    assert result["full_name"] == "John Doe"
    assert result["email"] == "john@example.com"
    assert result["phone"] == "123-456-7890"
    assert result["location"] == "New York, NY"
    assert len(result["experience"]) == 1
    assert len(result["skills"]) == 3
    assert len(result["certifications"]) == 1

def test_generate_profile_summary(ai_processor, mock_groq_client):
    # Test data
    profile_data = {
        "full_name": "John Doe",
        "experience": ["Senior Engineer at Tech Corp"],
        "skills": ["Python", "JavaScript", "AWS"]
    }
    
    # Mock the summary response
    mock_groq_client.chat.completions.create.return_value.choices[0].message.content = (
        "Experienced software engineer with expertise in Python, JavaScript, and AWS. "
        "Led development teams at Tech Corp, delivering innovative solutions."
    )
    
    # Call the method
    result = ai_processor.generate_profile_summary(profile_data)
    
    # Verify the result
    assert isinstance(result, str)
    assert len(result) > 0
    assert "software engineer" in result.lower()

def test_optimize_bullet_points(ai_processor, mock_groq_client):
    # Test data
    text = "Led team of 5 developers\nImplemented new features"
    job_description = "Looking for a team leader with experience in agile development"
    
    # Mock the optimization response
    mock_groq_client.chat.completions.create.return_value.choices[0].message.content = (
        "Led and mentored a team of 5 developers using agile methodologies\n"
        "Successfully implemented 10+ new features following best practices"
    )
    
    # Call the method
    result = ai_processor.optimize_bullet_points(text, job_description)
    
    # Verify the result
    assert isinstance(result, list)
    assert len(result) == 2
    assert "agile" in result[0].lower()
    assert "implemented" in result[1].lower()

def test_generate_resume(ai_processor, mock_groq_client):
    # Test data
    profile_data = {
        "full_name": "John Doe",
        "experience": ["Senior Engineer at Tech Corp"],
        "skills": ["Python", "JavaScript", "AWS"]
    }
    
    # Mock the resume response
    mock_groq_client.chat.completions.create.return_value.choices[0].message.content = (
        "JOHN DOE\n\n"
        "EXPERIENCE\n"
        "Senior Engineer at Tech Corp\n\n"
        "SKILLS\n"
        "Python, JavaScript, AWS"
    )
    
    # Call the method
    result = ai_processor.generate_resume(profile_data)
    
    # Verify the result
    assert isinstance(result, str)
    assert "JOHN DOE" in result
    assert "EXPERIENCE" in result
    assert "SKILLS" in result

def test_error_handling(ai_processor, mock_groq_client):
    # Test error handling when Groq API fails
    mock_groq_client.chat.completions.create.side_effect = Exception("API Error")
    
    # Test extract_resume_data
    result = ai_processor.extract_resume_data("test")
    assert result == {}
    
    # Test generate_profile_summary
    result = ai_processor.generate_profile_summary({})
    assert result == ""
    
    # Test optimize_bullet_points
    result = ai_processor.optimize_bullet_points("test", "test")
    assert result == []
    
    # Test generate_resume
    result = ai_processor.generate_resume({})
    assert result == "" 