"""
Standardized API Response Models
"""
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List, Dict, Any

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""
    ok: bool
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response with metadata"""
    ok: bool
    data: List[T]
    pagination: Dict[str, Any]
    total: int
    page: int
    limit: int
    has_more: bool

class ErrorResponse(BaseModel):
    """Error response format"""
    ok: bool = False
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None

