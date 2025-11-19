"""
Project service layer
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_, Integer
import sqlalchemy as sa
from typing import Optional, List, Tuple
from datetime import datetime
import uuid

from models.task import Project, ProjectCollaborator, Task
from models.user import User
from models.schemas.project import ProjectCreate, ProjectUpdate
import logging

logger = logging.getLogger(__name__)


class ProjectService:
    """Project service"""
    
    @staticmethod
    async def create_project(
        db: AsyncSession,
        user_id: uuid.UUID,
        project_data: ProjectCreate
    ) -> Project:
        """Create a new project"""
        project = Project(
            id=uuid.uuid4(),
            user_id=user_id,
            name=project_data.name,
            description=project_data.description,
            color=project_data.color,
            parent_project_id=project_data.parent_project_id,
            is_archived=False,
        )
        
        db.add(project)
        
        # Add creator as owner collaborator
        collaborator = ProjectCollaborator(
            project_id=project.id,
            user_id=user_id,
            role='owner',
            status='accepted',
            invited_by=user_id
        )
        db.add(collaborator)
        
        await db.commit()
        await db.refresh(project)
        
        logger.info(f"Project created: {project.id} by user {user_id}")
        return project
    
    @staticmethod
    async def get_project(
        db: AsyncSession,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Optional[Project]:
        """Get a project by ID (with access check)"""
        # Check if user has access to project
        result = await db.execute(
            select(Project)
            .join(ProjectCollaborator, Project.id == ProjectCollaborator.project_id)
            .where(
                and_(
                    Project.id == project_id,
                    ProjectCollaborator.user_id == user_id,
                    ProjectCollaborator.status == 'accepted'
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_projects(
        db: AsyncSession,
        user_id: uuid.UUID,
        include_archived: bool = False,
        parent_project_id: Optional[uuid.UUID] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[Project], int]:
        """Get projects with filtering and pagination"""
        # Base query - get projects where user is a collaborator
        query = (
            select(Project)
            .join(ProjectCollaborator, Project.id == ProjectCollaborator.project_id)
            .where(
                and_(
                    ProjectCollaborator.user_id == user_id,
                    ProjectCollaborator.status == 'accepted'
                )
            )
        )
        
        # Apply filters
        if not include_archived:
            query = query.where(Project.is_archived == False)
        
        if parent_project_id is not None:
            query = query.where(Project.parent_project_id == parent_project_id)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply sorting and pagination
        query = query.order_by(Project.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        result = await db.execute(query)
        projects = result.scalars().all()
        
        return list(projects), total
    
    @staticmethod
    async def update_project(
        db: AsyncSession,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        project_data: ProjectUpdate
    ) -> Optional[Project]:
        """Update a project (requires editor or owner role)"""
        # Check if user has edit permission
        if not await ProjectService.check_permission(db, project_id, user_id, ['owner', 'editor']):
            return None
        
        project = await ProjectService.get_project(db, project_id, user_id)
        if not project:
            return None
        
        # Update fields
        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        project.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(project)
        
        logger.info(f"Project updated: {project.id}")
        return project
    
    @staticmethod
    async def delete_project(
        db: AsyncSession,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """Delete a project (requires owner role)"""
        # Check if user is owner
        if not await ProjectService.check_permission(db, project_id, user_id, ['owner']):
            return False
        
        project = await ProjectService.get_project(db, project_id, user_id)
        if not project:
            return False
        
        await db.delete(project)
        await db.commit()
        
        logger.info(f"Project deleted: {project_id}")
        return True
    
    @staticmethod
    async def archive_project(
        db: AsyncSession,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        archived: bool = True
    ) -> Optional[Project]:
        """Archive or unarchive a project"""
        if not await ProjectService.check_permission(db, project_id, user_id, ['owner', 'editor']):
            return None
        
        project = await ProjectService.get_project(db, project_id, user_id)
        if not project:
            return None
        
        project.is_archived = archived
        project.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(project)
        
        logger.info(f"Project {'archived' if archived else 'unarchived'}: {project_id}")
        return project
    
    @staticmethod
    async def get_project_progress(
        db: AsyncSession,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Optional[dict]:
        """Calculate project progress based on tasks"""
        # Check access
        project = await ProjectService.get_project(db, project_id, user_id)
        if not project:
            return None
        
        # Get task counts
        result = await db.execute(
            select(
                func.count(Task.id).label('total'),
                func.sum(func.cast(Task.status == 'completed', sa.Integer)).label('completed'),
                func.sum(func.cast(Task.status == 'in_progress', sa.Integer)).label('in_progress'),
                func.sum(func.cast(Task.status == 'pending', sa.Integer)).label('pending'),
                func.sum(func.cast(
                    and_(
                        Task.due_date < datetime.utcnow(),
                        Task.status != 'completed'
                    ),
                    sa.Integer
                )).label('overdue')
            )
            .where(Task.project_id == project_id)
        )
        
        stats = result.one()
        total = stats.total or 0
        completed = stats.completed or 0
        
        progress_percentage = (completed / total * 100) if total > 0 else 0.0
        
        return {
            'project_id': project_id,
            'total_tasks': total,
            'completed_tasks': completed,
            'in_progress_tasks': stats.in_progress or 0,
            'pending_tasks': stats.pending or 0,
            'overdue_tasks': stats.overdue or 0,
            'progress_percentage': round(progress_percentage, 2)
        }
    
    @staticmethod
    async def get_child_projects(
        db: AsyncSession,
        parent_project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> List[Project]:
        """Get child projects of a parent project"""
        result = await db.execute(
            select(Project)
            .join(ProjectCollaborator, Project.id == ProjectCollaborator.project_id)
            .where(
                and_(
                    Project.parent_project_id == parent_project_id,
                    ProjectCollaborator.user_id == user_id,
                    ProjectCollaborator.status == 'accepted',
                    Project.is_archived == False
                )
            )
            .order_by(Project.created_at.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def check_permission(
        db: AsyncSession,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        required_roles: List[str]
    ) -> bool:
        """Check if user has required permission for project"""
        result = await db.execute(
            select(ProjectCollaborator)
            .where(
                and_(
                    ProjectCollaborator.project_id == project_id,
                    ProjectCollaborator.user_id == user_id,
                    ProjectCollaborator.status == 'accepted',
                    ProjectCollaborator.role.in_(required_roles)
                )
            )
        )
        return result.scalar_one_or_none() is not None
    
    # Collaborator methods
    
    @staticmethod
    async def add_collaborator(
        db: AsyncSession,
        project_id: uuid.UUID,
        inviter_id: uuid.UUID,
        invitee_email: str,
        role: str = 'viewer'
    ) -> Optional[ProjectCollaborator]:
        """Add a collaborator to a project"""
        # Check if inviter has permission
        if not await ProjectService.check_permission(db, project_id, inviter_id, ['owner', 'editor']):
            return None
        
        # Get invitee user
        result = await db.execute(
            select(User).where(User.email == invitee_email)
        )
        invitee = result.scalar_one_or_none()
        if not invitee:
            raise ValueError(f"User with email {invitee_email} not found")
        
        # Check if already a collaborator
        result = await db.execute(
            select(ProjectCollaborator).where(
                and_(
                    ProjectCollaborator.project_id == project_id,
                    ProjectCollaborator.user_id == invitee.id
                )
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError("User is already a collaborator")
        
        # Create collaborator
        collaborator = ProjectCollaborator(
            project_id=project_id,
            user_id=invitee.id,
            role=role,
            status='pending',
            invited_by=inviter_id
        )
        
        db.add(collaborator)
        await db.commit()
        await db.refresh(collaborator)
        
        logger.info(f"Collaborator added to project {project_id}: {invitee.id}")
        return collaborator
    
    @staticmethod
    async def update_collaborator_role(
        db: AsyncSession,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        collaborator_id: uuid.UUID,
        new_role: str
    ) -> Optional[ProjectCollaborator]:
        """Update collaborator role (requires owner)"""
        if not await ProjectService.check_permission(db, project_id, user_id, ['owner']):
            return None
        
        result = await db.execute(
            select(ProjectCollaborator).where(
                and_(
                    ProjectCollaborator.project_id == project_id,
                    ProjectCollaborator.user_id == collaborator_id
                )
            )
        )
        collaborator = result.scalar_one_or_none()
        if not collaborator:
            return None
        
        collaborator.role = new_role
        collaborator.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(collaborator)
        
        return collaborator
    
    @staticmethod
    async def remove_collaborator(
        db: AsyncSession,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        collaborator_id: uuid.UUID
    ) -> bool:
        """Remove a collaborator (requires owner)"""
        if not await ProjectService.check_permission(db, project_id, user_id, ['owner']):
            return False
        
        result = await db.execute(
            select(ProjectCollaborator).where(
                and_(
                    ProjectCollaborator.project_id == project_id,
                    ProjectCollaborator.user_id == collaborator_id
                )
            )
        )
        collaborator = result.scalar_one_or_none()
        if not collaborator:
            return False
        
        # Don't allow removing the owner
        if collaborator.role == 'owner':
            return False
        
        await db.delete(collaborator)
        await db.commit()
        
        logger.info(f"Collaborator removed from project {project_id}: {collaborator_id}")
        return True
    
    @staticmethod
    async def get_collaborators(
        db: AsyncSession,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> List[ProjectCollaborator]:
        """Get all collaborators for a project"""
        # Check access
        if not await ProjectService.check_permission(db, project_id, user_id, ['owner', 'editor', 'viewer']):
            return []
        
        result = await db.execute(
            select(ProjectCollaborator)
            .where(ProjectCollaborator.project_id == project_id)
            .order_by(ProjectCollaborator.created_at.asc())
        )
        return list(result.scalars().all())
