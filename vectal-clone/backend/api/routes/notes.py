"""
Note API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
import math

from models.schemas.note import (
    NoteCreate,
    NoteUpdate,
    NoteResponse,
    NoteListResponse,
    NoteVersionResponse,
    NoteSearchResponse,
    NoteSearchListResponse
)
from services.note_service import NoteService
from api.dependencies.auth import get_current_user
from models.user import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new note"""
    try:
        note = await NoteService.create_note(str(current_user.id), note_data)
        
        response = NoteResponse(**note.model_dump())
        response.preview = NoteService._generate_preview(note.content)
        response.word_count = len(note.content.split())
        
        return response
    except Exception as e:
        logger.error(f"Error creating note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create note"
        )


@router.get("", response_model=NoteListResponse)
async def get_notes(
    project_id: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),  # Comma-separated
    is_pinned: Optional[bool] = Query(None),
    is_archived: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """Get notes with filtering and pagination"""
    try:
        # Parse tags
        tag_list = tags.split(",") if tags else None
        
        notes, total = await NoteService.get_notes(
            str(current_user.id),
            project_id,
            tag_list,
            is_pinned,
            is_archived,
            page,
            page_size
        )
        
        # Convert to response
        note_responses = []
        for note in notes:
            response = NoteResponse(**note.model_dump())
            response.preview = NoteService._generate_preview(note.content)
            response.word_count = len(note.content.split())
            note_responses.append(response)
        
        total_pages = math.ceil(total / page_size)
        
        return NoteListResponse(
            items=note_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        logger.error(f"Error getting notes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get notes"
        )


@router.get("/search", response_model=NoteSearchListResponse)
async def search_notes(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """Search notes with full-text search"""
    try:
        results, total = await NoteService.search_notes(
            str(current_user.id),
            q,
            page,
            page_size
        )
        
        search_responses = [NoteSearchResponse(**result) for result in results]
        
        return NoteSearchListResponse(
            items=search_responses,
            total=total,
            query=q
        )
    except Exception as e:
        logger.error(f"Error searching notes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search notes"
        )


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific note"""
    note = await NoteService.get_note(note_id, str(current_user.id))
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    response = NoteResponse(**note.model_dump())
    response.preview = NoteService._generate_preview(note.content)
    response.word_count = len(note.content.split())
    
    return response


@router.patch("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    note_data: NoteUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a note"""
    note = await NoteService.update_note(note_id, str(current_user.id), note_data)
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    response = NoteResponse(**note.model_dump())
    response.preview = NoteService._generate_preview(note.content)
    response.word_count = len(note.content.split())
    
    return response


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a note"""
    success = await NoteService.delete_note(note_id, str(current_user.id))
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    return None


@router.get("/{note_id}/versions", response_model=List[NoteVersionResponse])
async def get_note_versions(
    note_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get version history for a note"""
    versions = await NoteService.get_note_versions(note_id, str(current_user.id))
    
    return [NoteVersionResponse(**v.model_dump()) for v in versions]


@router.get("/{note_id}/links")
async def get_note_links(
    note_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all linked entities (tasks and notes)"""
    links = await NoteService.get_linked_entities(note_id, str(current_user.id))
    
    if links is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    return links


@router.post("/{note_id}/render")
async def render_note_markdown(
    note_id: str,
    current_user: User = Depends(get_current_user)
):
    """Render note markdown to HTML"""
    note = await NoteService.get_note(note_id, str(current_user.id))
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    html = NoteService.render_markdown(note.content)
    
    return {"html": html}
