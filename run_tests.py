import pytest
import sys
import os

def main():
    """Run the test suite with coverage reporting."""
    # Get the directory containing this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Run pytest with coverage
    args = [
        "--cov=backend",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--verbose",
        "tests/"
    ]
    
    # Add any command line arguments
    args.extend(sys.argv[1:])
    
    # Run the tests
    return pytest.main(args)

if __name__ == "__main__":
    sys.exit(main())