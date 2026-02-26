"""Error handling utilities."""
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
from app.schemas import ErrorResponse, ErrorDetail


class AppException(HTTPException):
    """Custom application exception."""
    
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.details = details or {}
        super().__init__(status_code=status_code, detail=message)


def create_error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """Create a standardized error response."""
    return ErrorResponse(
        error=ErrorDetail(
            code=error_code,
            message=message,
            details=details or {}
        )
    )


# Common error exceptions
class UnauthorizedError(AppException):
    """401 Unauthorized error."""
    def __init__(self, message: str = "Invalid authentication credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
            message=message
        )


class ForbiddenError(AppException):
    """403 Forbidden error."""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
            message=message
        )


class NotFoundError(AppException):
    """404 Not Found error."""
    def __init__(self, resource: str = "Resource", resource_id: Optional[str] = None):
        message = f"{resource} not found"
        if resource_id:
            message += f" (ID: {resource_id})"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message=message
        )


class ValidationError(AppException):
    """422 Validation error."""
    def __init__(self, message: str = "Validation error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            message=message,
            details=details
        )


class ConflictError(AppException):
    """409 Conflict error."""
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            message=message
        )


class RateLimitError(AppException):
    """429 Rate limit error."""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="TOO_MANY_REQUESTS",
            message=message
        )
