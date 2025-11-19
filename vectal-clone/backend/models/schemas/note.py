"""
Note Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class NoteCreate(BaseModel):
    """Note creation schema"""
    title: str = Field(..., min_length=1, max_length=500)
    content: str
    project_id: Optional[str] = None
    tags: Optional[List[str]] = []
    linked_tasks: Optional[List[str]] = []
    linked_notes: Optional[List[str]] = []


class NoteUpdate(BaseModel):
    """Note update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = None
    project_id: Optional[str] = None
    tags: Optional[List[str]] = None
    linked_tasks: Optional[List[str]] = None
    linked_notes: Optional[List[str]] = None
    is_pinned: Optional[bool] = None
    is_archived: Optional[bool] = None


class NoteVersionResponse(BaseModel):
    """Note version response"""
    version: int
    content: str
    updated_at: datetime
    updated_by: str


class NoteLinkResponse(BaseModel):
    """Linked entity response"""
    entity_type: str
    entity_id: str
    title: Optional[str] = None


class NoteResponse(BaseModel):
    """Note response schema"""
    id: str
    user_id: str
    project_id: Optional[str]
    title: str
    content: str
    tags: List[str]
    linked_tasks: List[str]
    linked_notes: List[str]
    current_version: int
    is_pinned: bool
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    preview: Optional[str] = None  # First 200 chars
    word_count: Optional[int] = None
    
    class Config:
        from_attributes = True


class NoteListResponse(BaseModel):
    """Paginated note list response"""
    items: List[NoteResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class NoteSearchResponse(BaseModel):
    """Note search result"""
    id: str
    title: str
    content: str
    preview: str
    score: float
    highlights: List[str] = []
    tags: List[str]
    created_at: datetime
    updated_at: datetime


class NoteSearchListResponse(BaseModel):
    """Note search results list"""
    items: List[NoteSearchResponse]
    total: int
    query: str
