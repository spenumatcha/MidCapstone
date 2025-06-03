import PyPDF2
from docx import Document
from typing import Optional, Tuple
import os
from PIL import Image
import io

class FileUtils:
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF file content."""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
            return ""

    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        """Extract text from DOCX file content."""
        try:
            docx_file = io.BytesIO(file_content)
            doc = Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from DOCX: {str(e)}")
            return ""

    @staticmethod
    def process_uploaded_file(file_content: bytes, file_type: str) -> Tuple[str, Optional[str]]:
        """Process uploaded file and return extracted text and any error message."""
        if file_type == "application/pdf":
            text = FileUtils.extract_text_from_pdf(file_content)
            error = None if text else "Failed to extract text from PDF"
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = FileUtils.extract_text_from_docx(file_content)
            error = None if text else "Failed to extract text from DOCX"
        else:
            text = ""
            error = "Unsupported file type. Please upload PDF or DOCX files only."
        
        return text, error

    @staticmethod
    def process_profile_image(image_content: bytes) -> Tuple[Optional[bytes], Optional[str]]:
        """Process and validate profile image."""
        try:
            # Open image using PIL
            image = Image.open(io.BytesIO(image_content))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large (max 800x800)
            max_size = (800, 800)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85)
            return output.getvalue(), None
            
        except Exception as e:
            return None, f"Error processing image: {str(e)}"

    @staticmethod
    def save_temp_file(content: bytes, extension: str) -> Optional[str]:
        """Save temporary file and return the file path."""
        try:
            temp_dir = "temp"
            os.makedirs(temp_dir, exist_ok=True)
            
            import uuid
            filename = f"{uuid.uuid4()}.{extension}"
            filepath = os.path.join(temp_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(content)
            
            return filepath
        except Exception as e:
            print(f"Error saving temporary file: {str(e)}")
            return None

    @staticmethod
    def cleanup_temp_files():
        """Clean up temporary files."""
        try:
            temp_dir = "temp"
            if os.path.exists(temp_dir):
                for filename in os.listdir(temp_dir):
                    filepath = os.path.join(temp_dir, filename)
                    try:
                        os.remove(filepath)
                    except Exception as e:
                        print(f"Error removing file {filepath}: {str(e)}")
        except Exception as e:
            print(f"Error cleaning up temporary files: {str(e)}") 