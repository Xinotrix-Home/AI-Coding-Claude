"""
Note MongoDB models
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


class NoteVersion(BaseModel):
    """Note version for history tracking"""
    version: int
    content: str
    updated_at: datetime
    updated_by: str  # user_id


class NoteLink(BaseModel):
    """Link to another entity (task or note)"""
    entity_type: str  # 'task' or 'note'
    entity_id: str
    title: Optional[str] = None


class Note(BaseModel):
    """Note document model for MongoDB"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    project_id: Optional[str] = None
    
    # Content
    title: str
    content: str  # Markdown content
    tags: List[str] = Field(default_factory=list)
    
    # Links
    linked_tasks: List[str] = Field(default_factory=list)  # Task IDs
    linked_notes: List[str] = Field(default_factory=list)  # Note IDs
    
    # Version history
    versions: List[NoteVersion] = Field(default_factory=list)
    current_version: int = 1
    
    # Metadata
    is_pinned: bool = False
    is_archived: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440001",
                "project_id": "550e8400-e29b-41d4-a716-446655440002",
                "title": "Meeting Notes",
                "content": "# Meeting Notes\n\n- Discussed project timeline\n- Assigned tasks",
                "tags": ["meeting", "important"],
                "linked_tasks": ["550e8400-e29b-41d4-a716-446655440003"],
                "linked_notes": [],
                "versions": [],
                "current_version": 1,
                "is_pinned": False,
                "is_archived": False
            }
        }
