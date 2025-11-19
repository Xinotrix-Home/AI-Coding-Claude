"""
Project API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid
import math

from db.postgres import get_db
from models.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    ProjectProgressResponse,
    CollaboratorCreate,
    CollaboratorUpdate,
    CollaboratorResponse,
    ProjectWithCollaborators
)
from services.project_service import ProjectService
from api.dependencies.auth import get_current_user
from models.user import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new project"""
    try:
        project = await ProjectService.create_project(db, current_user.id, project_data)
        
        # Get progress
        progress = await ProjectService.get_project_progress(db, project.id, current_user.id)
        
        response = ProjectResponse.model_validate(project)
        if progress:
            response.task_count = progress['total_tasks']
            response.completed_task_count = progress['completed_tasks']
            response.progress_percentage = progress['progress_percentage']
        
        return response
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project"
        )


@router.get("", response_model=ProjectListResponse)
async def get_projects(
    include_archived: bool = Query(False),
    parent_project_id: Optional[uuid.UUID] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get projects with filtering and pagination"""
    try:
        projects, total = await ProjectService.get_projects(
            db, current_user.id, include_archived, parent_project_id, page, page_size
        )
        
        # Get progress for each project
        project_responses = []
        for project in projects:
            progress = await ProjectService.get_project_progress(db, project.id, current_user.id)
            project_response = ProjectResponse.model_validate(project)
            if progress:
                project_response.task_count = progress['total_tasks']
                project_response.completed_task_count = progress['completed_tasks']
                project_response.progress_percentage = progress['progress_percentage']
            project_responses.append(project_response)
        
        total_pages = math.ceil(total / page_size)
        
        return ProjectListResponse(
            items=project_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get projects"
        )


@router.get("/{project_id}", response_model=ProjectWithCollaborators)
async def get_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific project with collaborators"""
    project = await ProjectService.get_project(db, project_id, current_user.id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get progress
    progress = await ProjectService.get_project_progress(db, project.id, current_user.id)
    
    # Get collaborators
    collaborators = await ProjectService.get_collaborators(db, project_id, current_user.id)
    
    response = ProjectWithCollaborators.model_validate(project)
    if progress:
        response.task_count = progress['total_tasks']
        response.completed_task_count = progress['completed_tasks']
        response.progress_percentage = progress['progress_percentage']
    
    response.collaborators = [CollaboratorResponse.model_validate(c) for c in collaborators]
    
    return response


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a project"""
    project = await ProjectService.update_project(db, project_id, current_user.id, project_data)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or insufficient permissions"
        )
    
    # Get progress
    progress = await ProjectService.get_project_progress(db, project.id, current_user.id)
    
    response = ProjectResponse.model_validate(project)
    if progress:
        response.task_count = progress['total_tasks']
        response.completed_task_count = progress['completed_tasks']
        response.progress_percentage = progress['progress_percentage']
    
    return response


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a project"""
    success = await ProjectService.delete_project(db, project_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or insufficient permissions"
        )
    
    return None


@router.post("/{project_id}/archive", response_model=ProjectResponse)
async def archive_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Archive a project"""
    project = await ProjectService.archive_project(db, project_id, current_user.id, True)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or insufficient permissions"
        )
    
    return ProjectResponse.model_validate(project)


@router.post("/{project_id}/unarchive", response_model=ProjectResponse)
async def unarchive_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unarchive a project"""
    project = await ProjectService.archive_project(db, project_id, current_user.id, False)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or insufficient permissions"
        )
    
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}/progress", response_model=ProjectProgressResponse)
async def get_project_progress(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get project progress statistics"""
    progress = await ProjectService.get_project_progress(db, project_id, current_user.id)
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return ProjectProgressResponse(**progress)


@router.get("/{project_id}/tasks")
async def get_project_tasks(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all tasks for a project"""
    from services.task_service import TaskService
    from models.schemas.task import TaskFilter
    
    # Check project access
    project = await ProjectService.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get tasks
    filters = TaskFilter(project_id=project_id)
    tasks, total = await TaskService.get_tasks(db, current_user.id, filters, 1, 1000)
    
    # Get labels for each task
    from models.schemas.task import TaskResponse
    task_responses = []
    for task in tasks:
        labels = await TaskService.get_task_labels(db, task.id)
        task_response = TaskResponse.model_validate(task)
        task_response.labels = labels
        task_responses.append(task_response)
    
    return {
        "items": task_responses,
        "total": total
    }


@router.get("/{project_id}/children", response_model=ProjectListResponse)
async def get_child_projects(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get child projects of a parent project"""
    # Check parent project access
    parent = await ProjectService.get_project(db, project_id, current_user.id)
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent project not found"
        )
    
    children = await ProjectService.get_child_projects(db, project_id, current_user.id)
    
    # Get progress for each child
    project_responses = []
    for project in children:
        progress = await ProjectService.get_project_progress(db, project.id, current_user.id)
        project_response = ProjectResponse.model_validate(project)
        if progress:
            project_response.task_count = progress['total_tasks']
            project_response.completed_task_count = progress['completed_tasks']
            project_response.progress_percentage = progress['progress_percentage']
        project_responses.append(project_response)
    
    return ProjectListResponse(
        items=project_responses,
        total=len(project_responses),
        page=1,
        page_size=len(project_responses),
        total_pages=1
    )


# Collaborator endpoints

@router.post("/{project_id}/share", response_model=CollaboratorResponse, status_code=status.HTTP_201_CREATED)
async def add_collaborator(
    project_id: uuid.UUID,
    collaborator_data: CollaboratorCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a collaborator to a project"""
    try:
        collaborator = await ProjectService.add_collaborator(
            db, project_id, current_user.id, collaborator_data.user_email, collaborator_data.role
        )
        
        if not collaborator:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to add collaborators"
            )
        
        return CollaboratorResponse.model_validate(collaborator)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding collaborator: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add collaborator"
        )


@router.get("/{project_id}/collaborators", response_model=list[CollaboratorResponse])
async def get_collaborators(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all collaborators for a project"""
    collaborators = await ProjectService.get_collaborators(db, project_id, current_user.id)
    
    if not collaborators and not await ProjectService.get_project(db, project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return [CollaboratorResponse.model_validate(c) for c in collaborators]


@router.patch("/{project_id}/collaborators/{collaborator_id}", response_model=CollaboratorResponse)
async def update_collaborator(
    project_id: uuid.UUID,
    collaborator_id: uuid.UUID,
    collaborator_data: CollaboratorUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a collaborator's role"""
    collaborator = await ProjectService.update_collaborator_role(
        db, project_id, current_user.id, collaborator_id, collaborator_data.role
    )
    
    if not collaborator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaborator not found or insufficient permissions"
        )
    
    return CollaboratorResponse.model_validate(collaborator)


@router.delete("/{project_id}/collaborators/{collaborator_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_collaborator(
    project_id: uuid.UUID,
    collaborator_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a collaborator from a project"""
    success = await ProjectService.remove_collaborator(db, project_id, current_user.id, collaborator_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaborator not found or insufficient permissions"
        )
    
    return None
