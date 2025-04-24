import os
import shutil
from typing import Optional
from fastapi import UploadFile, HTTPException
import uuid
import magic

from app.config import settings

# Allowed file types and their MIME types
ALLOWED_EXTENSIONS = {
    'pdf': 'application/pdf',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'doc': 'application/msword',
    'txt': 'text/plain',
    'rtf': 'application/rtf',
}

def save_upload_file(upload_file: UploadFile, directory: Optional[str] = None) -> tuple[str, str]:
    """
    Saves an uploaded file to the specified directory and returns the file path.
    
    Args:
        upload_file: The uploaded file
        directory: Optional subdirectory within UPLOAD_DIR
    
    Returns:
        Tuple of (file_path, file_type)
    """
    # Check if the file type is allowed
    content_type = magic.from_buffer(upload_file.file.read(2048), mime=True)
    upload_file.file.seek(0)  # Reset file position after reading
    
    file_extension = os.path.splitext(upload_file.filename)[1].lower().lstrip('.')
    
    if file_extension not in ALLOWED_EXTENSIONS or content_type not in ALLOWED_EXTENSIONS.values():
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS.keys())}"
        )
    
    # Create a unique filename
    unique_filename = f"{uuid.uuid4()}_{upload_file.filename}"
    
    # Determine save directory
    save_dir = settings.UPLOAD_DIR
    if directory:
        save_dir = os.path.join(save_dir, directory)
        os.makedirs(save_dir, exist_ok=True)
    
    # Create full file path
    file_path = os.path.join(save_dir, unique_filename)
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return file_path, file_extension

def remove_file(file_path: str) -> bool:
    """
    Removes a file from the filesystem.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False