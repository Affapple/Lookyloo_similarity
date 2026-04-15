from typing import Callable, Any, List
from fastapi import UploadFile, HTTPException

# Registry for validation functions
VALIDATION_FUNCTIONS: List[Callable[[UploadFile], None]] = []

def validator(func: Callable[[UploadFile], Any]):
    """
    Decorator to register a function as a validator.
    Each validator should take an UploadFile and raise an HTTPException if invalid.
    """
    VALIDATION_FUNCTIONS.append(func)
    return func


async def validate_file(file: UploadFile):
    """
    Runs all registered validation functions on the file.
    """
    for validator_func in VALIDATION_FUNCTIONS:
        validator_func(file)
    
    # Reset file pointer after potential reads during validation
    await file.seek(0)


@validator
def validate_is_image(file: UploadFile):
    """Checks if the uploaded file is an image."""
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

@validator
def validate_size(file: UploadFile, max_size_mb: int = 100):
    """Checks if the uploaded file size is within limits."""

    file_size = getattr(file, 'size', None)
    if file_size is None:
        # Fallback to manual check
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
    if file_size > max_size_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File size exceeds {max_size_mb}MB limit")

