"""Custom exception classes for Fashion Tech API."""
from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base application exception."""
    def __init__(self, status_code: int, message: str):
        super().__init__(status_code=status_code, detail=message)


class ValidationError(AppException):
    """400 - Request validation failed."""
    def __init__(self, message: str = "Validation error"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, message=message)


class Unauthorized(AppException):
    """401 - Authentication required or failed."""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, message=message)


class Forbidden(AppException):
    """403 - Authenticated but not authorized."""
    def __init__(self, message: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, message=message)


class NotFound(AppException):
    """404 - Resource not found."""
    def __init__(self, message: str = "Not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, message=message)


class Conflict(AppException):
    """409 - Resource conflict (e.g. duplicate email)."""
    def __init__(self, message: str = "Conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, message=message)


# ─── Service-layer exceptions (not tied to HTTP, usable outside FastAPI) ─────

class ServiceError(Exception):
    """Base exception for service-layer errors."""
    def __init__(self, message: str, code: str | None = None):
        self.message = message
        self.code = code or self.__class__.__name__
        super().__init__(message)


class AuthError(ServiceError):
    """Authentication / JWT errors."""
    pass


class S3Error(ServiceError):
    """S3 / storage operation errors."""
    pass


class NotFoundError(ServiceError):
    """Resource not found (service layer)."""
    pass


class PermissionError(ServiceError):  # noqa: A001
    """Permission denied (service layer)."""
    pass


class GarmentError(ServiceError):
    """Garment business logic errors."""
    pass


class OutfitError(ServiceError):
    """Outfit CRUD errors."""
    pass
