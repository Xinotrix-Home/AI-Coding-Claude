"""
Project Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class ProjectCreate(BaseModel):
    """Project creation schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    parent_project_id: Optional[uuid.UUID] = None


class ProjectUpdate(BaseModel):
    """Project update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    parent_project_id: Optional[uuid.UUID] = None
    is_archived: Optional[bool] = None


class ProjectResponse(BaseModel):
    """Project response schema"""
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    description: Optional[str]
    color: Optional[str]
    parent_project_id: Optional[uuid.UUID]
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    task_count: Optional[int] = 0
    completed_task_count: Optional[int] = 0
    progress_percentage: Optional[float] = 0.0
    
    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Paginated project list response"""
    items: List[ProjectResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ProjectProgressResponse(BaseModel):
    """Project progress response"""
    project_id: uuid.UUID
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    pending_tasks: int
    progress_percentage: float
    overdue_tasks: int


class CollaboratorCreate(BaseModel):
    """Collaborator invitation schema"""
    user_email: str
    role: str = Field(default='viewer', pattern=r'^(owner|editor|viewer)$')


class CollaboratorUpdate(BaseModel):
    """Collaborator update schema"""
    role: str = Field(..., pattern=r'^(owner|editor|viewer)$')


class CollaboratorResponse(BaseModel):
    """Collaborator response schema"""
    project_id: uuid.UUID
    user_id: uuid.UUID
    role: str
    status: str
    invited_by: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    
    # User details
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProjectWithCollaborators(ProjectResponse):
    """Project with collaborators"""
    collaborators: List[CollaboratorResponse] = []
