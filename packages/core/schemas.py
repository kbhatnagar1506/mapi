from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum

class SourceType(str, Enum):
    """Source type enumeration"""
    CHAT = "chat"
    FILE = "file"
    URL = "url"

class MemoryWrite(BaseModel):
    """Memory write request with validation"""
    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Memory content text"
    )
    source: SourceType = Field(
        ...,
        description="Source type of the memory"
    )
    tags: List[str] = Field(
        default=[],
        max_items=20,
        description="Tags for categorization"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of the memory"
    )
    
    @validator('text')
    def text_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty or whitespace only')
        return v.strip()
    
    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 20:
            raise ValueError('Maximum 20 tags allowed')
        # Remove duplicates and empty tags
        return list(set([tag.strip() for tag in v if tag.strip()]))
    
    class Config:
        schema_extra = {
            "example": {
                "text": "User prefers dark mode",
                "source": "chat",
                "tags": ["preferences", "ui"]
            }
        }

class RetrievalQuery(BaseModel):
    """Retrieval query with validation"""
    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Query text"
    )
    as_of: Optional[datetime] = Field(
        None,
        description="Query facts as of this date (temporal reasoning)"
    )
    top_k: int = Field(
        None,
        ge=1,
        le=50,
        description="Number of results to return"
    )
    
    @validator('query')
    def query_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()
    
    def __init__(self, **data):
        from .advanced_config import DEFAULT_TOP_K
        if 'top_k' not in data or data['top_k'] is None:
            data['top_k'] = DEFAULT_TOP_K
        super().__init__(**data)
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What did I promise John?",
                "as_of": "2025-01-15T00:00:00Z",
                "top_k": 6
            }
        }

class Candidate(BaseModel):
    type: str
    score: float
    payload: Dict[str, Any]

class Answer(BaseModel):
    answer: str
    sources: List[Candidate]
    confidence: float
    notes: Optional[str] = None

class CorrectionRequest(BaseModel):
    """Correction request for continuous learning"""
    original_answer: str = Field(..., min_length=1, description="Original incorrect answer")
    correction: str = Field(..., min_length=1, description="Corrected answer")
    query: Optional[str] = Field(None, description="Original query that led to the error")
    
    @validator('original_answer', 'correction')
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError('Cannot be empty')
        return v.strip()

class ConsolidationRequest(BaseModel):
    """Memory consolidation request"""
    force: bool = Field(False, description="Force immediate consolidation")

