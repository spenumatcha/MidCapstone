# AI-Powered Portfolio & Resume Generator

An AI-driven web application that helps users create professional portfolios, ATS-ready resumes, and tailored cover letters using Groq and LLM technology.

## Features

- **Profile Builder**: Create your professional profile through multiple input methods:
  - Upload existing resume (PDF/DOCX)
  - LinkedIn profile integration (coming soon)
  - Manual data entry
- **Resume Generation**: Generate ATS-ready resumes in PDF format
- **Portfolio Creation**: Create a professional portfolio website (coming soon)
- **Cover Letter Generation**: Generate tailored cover letters (coming soon)

## Prerequisites

- Python 3.8 or higher
- Groq API key
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your Groq API key:
```
GROQ_API_KEY=your_api_key_here
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run frontend/app.py
```

2. Open your web browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

3. Follow the on-screen instructions to:
   - Upload your resume or enter your information manually
   - Review and edit extracted information
   - Generate your resume and portfolio

## Project Structure

```
.
├── backend/
│   ├── ai_processor.py    # AI processing and LLM interactions
│   └── file_utils.py      # File handling utilities
├── frontend/
│   └── app.py            # Streamlit web application
├── temp/                 # Temporary file storage
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Privacy & Security

- No user accounts required
- All data is processed in-memory and deleted after session ends
- No long-term storage of personal information
- Temporary files are automatically cleaned up

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.