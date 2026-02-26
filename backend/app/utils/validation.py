"""Input validation and sanitization utilities."""
import bleach
from typing import Optional


def sanitize_string(input_str: str, max_length: Optional[int] = None) -> str:
    """Sanitize a string input to prevent XSS attacks."""
    if not isinstance(input_str, str):
        return ""
    
    # Remove HTML tags and dangerous characters
    cleaned = bleach.clean(
        input_str,
        tags=[],  # Remove all HTML tags
        attributes={},
        strip=True
    )
    
    # Trim whitespace
    cleaned = cleaned.strip()
    
    # Apply max length if specified
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    return cleaned


def sanitize_text(input_str: str) -> str:
    """Sanitize text input (allows some basic formatting)."""
    if not isinstance(input_str, str):
        return ""
    
    # Allow basic formatting but remove scripts
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li']
    cleaned = bleach.clean(
        input_str,
        tags=allowed_tags,
        attributes={},
        strip=True
    )
    
    return cleaned.strip()
