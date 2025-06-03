import pytest
from unittest.mock import Mock, patch, mock_open
from backend.file_utils import FileUtils
import io
from PIL import Image
import os

@pytest.fixture
def sample_pdf_content():
    return b"%PDF-1.4\nTest PDF content"

@pytest.fixture
def sample_docx_content():
    # The content is irrelevant since Document will be mocked
    return b"irrelevant"

@pytest.fixture
def mock_docx_document():
    mock_doc = Mock()
    mock_paragraph = Mock()
    mock_paragraph.text = "Test DOCX content"
    mock_doc.paragraphs = [mock_paragraph]
    return mock_doc

@pytest.fixture
def sample_image_content():
    # Create a small test image
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

def test_extract_text_from_pdf(sample_pdf_content):
    with patch('PyPDF2.PdfReader') as mock_pdf_reader:
        # Mock PDF reader
        mock_page = Mock()
        mock_page.extract_text.return_value = "Test PDF content"
        mock_pdf_reader.return_value.pages = [mock_page]
        
        # Test the method
        result = FileUtils.extract_text_from_pdf(sample_pdf_content)
        assert result == "Test PDF content"

def test_extract_text_from_docx(sample_docx_content, mock_docx_document):
    with patch('backend.file_utils.Document', return_value=mock_docx_document) as mock_document:
        # Test the method
        result = FileUtils.extract_text_from_docx(sample_docx_content)
        assert result == "Test DOCX content"
        mock_document.assert_called_once()

def test_process_uploaded_file_pdf(sample_pdf_content):
    with patch('PyPDF2.PdfReader') as mock_pdf_reader:
        # Mock PDF reader
        mock_page = Mock()
        mock_page.extract_text.return_value = "Test PDF content"
        mock_pdf_reader.return_value.pages = [mock_page]
        
        # Test the method
        text, error = FileUtils.process_uploaded_file(sample_pdf_content, "application/pdf")
        assert text == "Test PDF content"
        assert error is None

def test_process_uploaded_file_docx(sample_docx_content, mock_docx_document):
    with patch('backend.file_utils.Document', return_value=mock_docx_document) as mock_document:
        # Test the method
        text, error = FileUtils.process_uploaded_file(
            sample_docx_content,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        assert text == "Test DOCX content"
        assert error is None
        mock_document.assert_called_once()

def test_process_uploaded_file_invalid():
    # Test with invalid file type
    text, error = FileUtils.process_uploaded_file(b"test", "invalid/type")
    assert text == ""
    assert error == "Unsupported file type. Please upload PDF or DOCX files only."

def test_process_profile_image(sample_image_content):
    # Test image processing
    processed_image, error = FileUtils.process_profile_image(sample_image_content)
    assert processed_image is not None
    assert error is None
    
    # Verify the processed image
    img = Image.open(io.BytesIO(processed_image))
    assert img.size[0] <= 800
    assert img.size[1] <= 800
    assert img.mode == 'RGB'

def test_process_profile_image_invalid():
    # Test with invalid image data
    processed_image, error = FileUtils.process_profile_image(b"invalid image data")
    assert processed_image is None
    assert "Error processing image" in error

def test_save_temp_file():
    with patch('os.makedirs') as mock_makedirs, \
         patch('uuid.uuid4') as mock_uuid, \
         patch('builtins.open', mock_open()) as mock_file:
        
        # Mock UUID
        mock_uuid.return_value = "test-uuid"
        
        # Test saving file
        content = b"test content"
        result = FileUtils.save_temp_file(content, "txt")
        
        # Verify the result
        assert result == os.path.join("temp", "test-uuid.txt")
        mock_makedirs.assert_called_once_with("temp", exist_ok=True)
        mock_file.assert_called_once_with(result, 'wb')
        mock_file().write.assert_called_once_with(content)

def test_cleanup_temp_files():
    with patch('os.path.exists') as mock_exists, \
         patch('os.listdir') as mock_listdir, \
         patch('os.remove') as mock_remove:
        
        # Mock directory exists and contains files
        mock_exists.return_value = True
        mock_listdir.return_value = ["file1.txt", "file2.txt"]
        
        # Test cleanup
        FileUtils.cleanup_temp_files()
        
        # Verify cleanup was attempted
        assert mock_remove.call_count == 2
        mock_exists.assert_called_once_with("temp")
        mock_listdir.assert_called_once_with("temp")

def test_cleanup_temp_files_no_directory():
    with patch('os.path.exists') as mock_exists, \
         patch('os.listdir') as mock_listdir:
        
        # Mock directory doesn't exist
        mock_exists.return_value = False
        
        # Test cleanup
        FileUtils.cleanup_temp_files()
        
        # Verify no cleanup was attempted
        mock_exists.assert_called_once_with("temp")
        mock_listdir.assert_not_called() 