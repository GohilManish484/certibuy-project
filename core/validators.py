from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
import os


ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_image_file(file):
    """Validate uploaded image files for security"""
    
    # Check file size
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(f'File size exceeds maximum limit of {MAX_FILE_SIZE / (1024 * 1024)}MB')
    
    # Check file extension
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(f'Invalid file type. Allowed types: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}')
    
    # Validate actual image content
    try:
        width, height = get_image_dimensions(file)
        if width is None or height is None:
            raise ValidationError('Invalid image file')
        
        # Check minimum dimensions
        if width < 50 or height < 50:
            raise ValidationError('Image dimensions too small (minimum 50x50 pixels)')
        
        # Check maximum dimensions
        if width > 5000 or height > 5000:
            raise ValidationError('Image dimensions too large (maximum 5000x5000 pixels)')
            
    except Exception as e:
        raise ValidationError(f'Cannot validate image file: {str(e)}')
    
    # Reset file pointer after reading
    file.seek(0)
    
    return file


def validate_image_content_type(file):
    """Validate image MIME type"""
    valid_content_types = ['image/jpeg', 'image/png', 'image/webp']
    
    if hasattr(file, 'content_type'):
        if file.content_type not in valid_content_types:
            raise ValidationError(f'Invalid content type. Allowed: {", ".join(valid_content_types)}')
    
    return file


def secure_filename(filename):
    """Generate secure filename to prevent path traversal"""
    import uuid
    import re
    
    # Remove any path components
    filename = os.path.basename(filename)
    
    # Get extension
    name, ext = os.path.splitext(filename)
    
    # Sanitize extension
    ext = ext.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        ext = '.jpg'
    
    # Generate unique name
    unique_name = f"{uuid.uuid4().hex}{ext}"
    
    return unique_name
