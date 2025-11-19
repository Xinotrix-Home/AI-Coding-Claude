"""
Note service layer
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List, Tuple
from datetime import datetime
import re
import markdown
from bs4 import BeautifulSoup

from models.note import Note, NoteVersion
from models.schemas.note import NoteCreate, NoteUpdate
from db.mongodb import get_collection, Collections
import logging

logger = logging.getLogger(__name__)


class NoteService:
    """Note service"""
    
    @staticmethod
    async def create_note(
        user_id: str,
        note_data: NoteCreate
    ) -> Note:
        """Create a new note"""
        note = Note(
            user_id=user_id,
            title=note_data.title,
            content=note_data.content,
            project_id=note_data.project_id,
            tags=note_data.tags or [],
            linked_tasks=note_data.linked_tasks or [],
            linked_notes=note_data.linked_notes or [],
            current_version=1,
            versions=[]
        )
        
        collection = get_collection(Collections.NOTES)
        await collection.insert_one(note.model_dump())
        
        # Create indexes if not exists
        await NoteService._ensure_indexes()
        
        logger.info(f"Note created: {note.id} by user {user_id}")
        return note
    
    @staticmethod
    async def get_note(
        note_id: str,
        user_id: str
    ) -> Optional[Note]:
        """Get a note by ID"""
        collection = get_collection(Collections.NOTES)
        
        note_dict = await collection.find_one({
            "id": note_id,
            "user_id": user_id
        })
        
        if note_dict:
            return Note(**note_dict)
        return None
    
    @staticmethod
    async def get_notes(
        user_id: str,
        project_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_pinned: Optional[bool] = None,
        is_archived: bool = False,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[Note], int]:
        """Get notes with filtering and pagination"""
        collection = get_collection(Collections.NOTES)
        
        # Build query
        query = {"user_id": user_id}
        
        if project_id:
            query["project_id"] = project_id
        
        if tags:
            query["tags"] = {"$in": tags}
        
        if is_pinned is not None:
            query["is_pinned"] = is_pinned
        
        query["is_archived"] = is_archived
        
        # Get total count
        total = await collection.count_documents(query)
        
        # Get paginated results
        skip = (page - 1) * page_size
        cursor = collection.find(query).sort("updated_at", -1).skip(skip).limit(page_size)
        
        notes = []
        async for note_dict in cursor:
            notes.append(Note(**note_dict))
        
        return notes, total
    
    @staticmethod
    async def update_note(
        note_id: str,
        user_id: str,
        note_data: NoteUpdate
    ) -> Optional[Note]:
        """Update a note and save version history"""
        collection = get_collection(Collections.NOTES)
        
        # Get existing note
        note = await NoteService.get_note(note_id, user_id)
        if not note:
            return None
        
        # Save current version to history if content changed
        if note_data.content and note_data.content != note.content:
            version = NoteVersion(
                version=note.current_version,
                content=note.content,
                updated_at=note.updated_at,
                updated_by=user_id
            )
            note.versions.append(version)
            note.current_version += 1
        
        # Update fields
        update_data = note_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(note, field, value)
        
        note.updated_at = datetime.utcnow()
        
        # Update in database
        await collection.update_one(
            {"id": note_id, "user_id": user_id},
            {"$set": note.model_dump()}
        )
        
        logger.info(f"Note updated: {note_id}")
        return note
    
    @staticmethod
    async def delete_note(
        note_id: str,
        user_id: str
    ) -> bool:
        """Delete a note"""
        collection = get_collection(Collections.NOTES)
        
        result = await collection.delete_one({
            "id": note_id,
            "user_id": user_id
        })
        
        if result.deleted_count > 0:
            logger.info(f"Note deleted: {note_id}")
            return True
        return False
    
    @staticmethod
    async def get_note_versions(
        note_id: str,
        user_id: str
    ) -> List[NoteVersion]:
        """Get version history for a note"""
        note = await NoteService.get_note(note_id, user_id)
        if not note:
            return []
        
        return note.versions
    
    @staticmethod
    async def get_linked_entities(
        note_id: str,
        user_id: str
    ) -> dict:
        """Get all linked tasks and notes"""
        note = await NoteService.get_note(note_id, user_id)
        if not note:
            return {"tasks": [], "notes": []}
        
        # Get linked notes
        linked_notes = []
        if note.linked_notes:
            collection = get_collection(Collections.NOTES)
            cursor = collection.find({
                "id": {"$in": note.linked_notes},
                "user_id": user_id
            })
            async for note_dict in cursor:
                linked_notes.append({
                    "id": note_dict["id"],
                    "title": note_dict["title"]
                })
        
        return {
            "tasks": note.linked_tasks,  # Task IDs
            "notes": linked_notes
        }
    
    @staticmethod
    async def search_notes(
        user_id: str,
        query: str,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[dict], int]:
        """Full-text search for notes"""
        collection = get_collection(Collections.NOTES)
        
        # Ensure text index exists
        await NoteService._ensure_indexes()
        
        # Build search query
        search_query = {
            "user_id": user_id,
            "$text": {"$search": query}
        }
        
        # Get total count
        total = await collection.count_documents(search_query)
        
        # Get paginated results with score
        skip = (page - 1) * page_size
        cursor = collection.find(
            search_query,
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).skip(skip).limit(page_size)
        
        results = []
        async for note_dict in cursor:
            # Generate preview with highlights
            preview = NoteService._generate_preview(note_dict["content"], query)
            highlights = NoteService._extract_highlights(note_dict["content"], query)
            
            results.append({
                "id": note_dict["id"],
                "title": note_dict["title"],
                "content": note_dict["content"],
                "preview": preview,
                "score": note_dict.get("score", 0),
                "highlights": highlights,
                "tags": note_dict.get("tags", []),
                "created_at": note_dict["created_at"],
                "updated_at": note_dict["updated_at"]
            })
        
        return results, total
    
    @staticmethod
    def render_markdown(content: str) -> str:
        """Render markdown to HTML"""
        html = markdown.markdown(
            content,
            extensions=['fenced_code', 'codehilite', 'tables', 'nl2br']
        )
        return html
    
    @staticmethod
    def _generate_preview(content: str, query: str = "", max_length: int = 200) -> str:
        """Generate preview text with query context"""
        # Remove markdown formatting
        text = re.sub(r'[#*`\[\]()]', '', content)
        text = ' '.join(text.split())
        
        if query:
            # Find query position and create context around it
            query_lower = query.lower()
            text_lower = text.lower()
            pos = text_lower.find(query_lower)
            
            if pos != -1:
                start = max(0, pos - 50)
                end = min(len(text), pos + len(query) + 150)
                preview = text[start:end]
                if start > 0:
                    preview = "..." + preview
                if end < len(text):
                    preview = preview + "..."
                return preview
        
        # Default preview
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text
    
    @staticmethod
    def _extract_highlights(content: str, query: str, max_highlights: int = 3) -> List[str]:
        """Extract highlighted snippets containing query"""
        highlights = []
        query_lower = query.lower()
        
        # Split into sentences
        sentences = re.split(r'[.!?]\s+', content)
        
        for sentence in sentences:
            if query_lower in sentence.lower() and len(highlights) < max_highlights:
                highlights.append(sentence.strip())
        
        return highlights
    
    @staticmethod
    async def _ensure_indexes():
        """Ensure MongoDB indexes exist"""
        collection = get_collection(Collections.NOTES)
        
        # Create indexes
        await collection.create_index("user_id")
        await collection.create_index("project_id")
        await collection.create_index("tags")
        await collection.create_index([("title", "text"), ("content", "text")])
        await collection.create_index("updated_at")
