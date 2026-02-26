"""File upload and download service for PDF resources."""
import uuid
import os
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException, status
from app.config import settings


def validate_pdf_file(file: UploadFile) -> Tuple[bool, Optional[str]]:
    """Validate that uploaded file is a PDF.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file extension
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        return False, "File must be a PDF (.pdf extension required)"
    
    # Check content type
    if file.content_type != "application/pdf":
        return False, "File must be of type application/pdf"
    
    return True, None


def validate_pdf_magic_bytes(file_content: bytes) -> bool:
    """Validate PDF using magic bytes (file signature)."""
    # Primary check: PDF files start with %PDF
    if len(file_content) < 4:
        return False
    
    if file_content[:4] != b'%PDF':
        return False
    
    # Optional: Use python-magic if available for additional validation
    try:
        import magic
        mime = magic.Magic(mime=True)
        detected_type = mime.from_buffer(file_content)
        return detected_type == "application/pdf"
    except (ImportError, Exception):
        # Fallback: if python-magic is not available, trust the %PDF signature
        return True


def save_pdf_file(file: UploadFile) -> Tuple[str, int]:
    """Save uploaded PDF file with GUID name.
    
    Returns:
        Tuple of (file_url, file_size)
    """
    # Read file content
    file_content = file.file.read()
    file_size = len(file_content)
    
    # Validate file size
    if file_size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB"
        )
    
    # Validate magic bytes
    if not validate_pdf_magic_bytes(file_content):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not a valid PDF"
        )
    
    # Generate GUID filename
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.pdf"
    
    # Ensure upload directory exists
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = upload_dir / filename
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Return relative path for database storage
    file_url = f"uploads/{filename}"
    
    return file_url, file_size


def get_file_path(file_url: str) -> Path:
    """Get full file path from database file_url."""
    return Path(file_url)


def delete_file(file_url: str) -> bool:
    """Delete a file from the filesystem.
    
    Returns:
        True if file was deleted, False if it didn't exist
    """
    file_path = Path(file_url)
    
    if file_path.exists() and file_path.is_file():
        file_path.unlink()
        return True
    
    return False


def file_exists(file_url: str) -> bool:
    """Check if a file exists."""
    file_path = Path(file_url)
    return file_path.exists() and file_path.is_file()
