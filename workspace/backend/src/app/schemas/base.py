"""Base response schemas."""
from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """Standard API response envelope."""
    status: str
    data: Optional[T] = None
    error: Optional[str] = None

    @classmethod
    def success(cls, data: Any) -> "BaseResponse":
        return cls(status="success", data=data, error=None)

    @classmethod
    def error(cls, message: str) -> "BaseResponse":
        return cls(status="error", data=None, error=message)


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response."""
    status: str = "success"
    data: list[T] = []
    error: Optional[str] = None
    total: int = 0
    limit: int = 20
    offset: int = 0
