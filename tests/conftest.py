import pytest
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup and teardown for each test."""
    # Create a temporary directory for test files
    os.makedirs("temp", exist_ok=True)
    
    yield
    
    # Cleanup after tests
    if os.path.exists("temp"):
        for file in os.listdir("temp"):
            try:
                os.remove(os.path.join("temp", file))
            except Exception:
                pass
        try:
            os.rmdir("temp")
        except Exception:
            pass

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    with pytest.MonkeyPatch.context() as m:
        m.setenv("GROQ_API_KEY", "test_api_key")
        yield 