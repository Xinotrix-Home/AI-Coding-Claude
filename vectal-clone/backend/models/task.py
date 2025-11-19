"""
Task database models
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from db.postgres import Base


class Task(Base):
    """Task model"""
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # Task details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default='pending', nullable=False)  # pending, in_progress, completed, cancelled
    priority = Column(Integer, default=0, nullable=False)  # 0=none, 1=low, 2=medium, 3=high, 4=urgent
    
    # Dates
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Recurrence
    recurrence_rule = Column(Text, nullable=True)  # RRULE format
    
    # Hierarchy
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='CASCADE'), nullable=True)
    position = Column(Integer, default=0)  # For ordering
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_task_user_status', 'user_id', 'status'),
        Index('idx_task_due_date', 'due_date'),
        Index('idx_task_project', 'project_id'),
        Index('idx_task_parent', 'parent_task_id'),
    )

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"


class TaskLabel(Base):
    """Task label model for categorization"""
    __tablename__ = "task_labels"

    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True)
    label = Column(String(100), primary_key=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_task_label', 'task_id', 'label'),
    )

    def __repr__(self):
        return f"<TaskLabel(task_id={self.task_id}, label={self.label})>"


class Project(Base):
    """Project model for organizing tasks"""
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Project details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    
    # Hierarchy
    parent_project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id', ondelete='CASCADE'), nullable=True)
    
    # Status
    is_archived = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_project_user', 'user_id'),
        Index('idx_project_parent', 'parent_project_id'),
    )

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name})>"


class ProjectCollaborator(Base):
    """Project collaborator model for team access"""
    __tablename__ = "project_collaborators"

    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    
    # Role-based access control
    role = Column(String(50), nullable=False, default='viewer')  # owner, editor, viewer
    
    # Invitation status
    status = Column(String(50), nullable=False, default='pending')  # pending, accepted, declined
    invited_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_collaborator_project', 'project_id'),
        Index('idx_collaborator_user', 'user_id'),
        Index('idx_collaborator_status', 'status'),
    )

    def __repr__(self):
        return f"<ProjectCollaborator(project_id={self.project_id}, user_id={self.user_id}, role={self.role})>"
