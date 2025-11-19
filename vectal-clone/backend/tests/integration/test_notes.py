"""
Integration tests for notes management
"""
import pytest
from httpx import AsyncClient
from models.user import User
from db.mongodb import get_collection, Collections


@pytest.fixture
async def cleanup_notes():
    """Cleanup notes collection after tests"""
    yield
    collection = get_collection(Collections.NOTES)
    await collection.delete_many({})


@pytest.mark.asyncio
class TestNoteCreation:
    """Test note creation endpoints"""
    
    async def test_create_note_success(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        cleanup_notes
    ):
        """Test successful note creation"""
        response = await client.post(
            "/api/v1/notes",
            json={
                "title": "Test Note",
                "content": "# Test Content\n\nThis is a test note.",
                "tags": ["test", "important"]
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["title"] == "Test Note"
        assert data["content"] == "# Test Content\n\nThis is a test note."
        assert "test" in data["tags"]
        assert "important" in data["tags"]
        assert "id" in data
        assert data["current_version"] == 1
    
    async def test_create_note_minimal(
        self,
        client: AsyncClient,
        auth_headers: dict,
        cleanup_notes
    ):
        """Test creating note with minimal data"""
        response = await client.post(
            "/api/v1/notes",
            json={
                "title": "Minimal Note",
                "content": "Simple content"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Minimal Note"
        assert data["tags"] == []
    
    async def test_create_note_with_links(
        self,
        client: AsyncClient,
        auth_headers: dict,
        cleanup_notes
    ):
        """Test creating note with task links"""
        response = await client.post(
            "/api/v1/notes",
            json={
                "title": "Linked Note",
                "content": "Note with links",
                "linked_tasks": ["task-id-1", "task-id-2"]
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data["linked_tasks"]) == 2
    
    async def test_create_note_without_auth(self, client: AsyncClient, cleanup_notes):
        """Test creating note without authentication"""
        response = await client.post(
            "/api/v1/notes",
            json={"title": "Test", "content": "Test"}
        )
        
        assert response.status_code == 403


@pytest.mark.asyncio
class TestNoteRetrieval:
    """Test note retrieval endpoints"""
    
    async def test_get_all_notes(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        cleanup_notes
    ):
        """Test getting all notes"""
        # Create test notes
        for i in range(3):
            await client.post(
                "/api/v1/notes",
                json={
                    "title": f"Note {i}",
                    "content": f"Content {i}"
                },
                headers=auth_headers
            )
        
        response = await client.get(
            "/api/v1/notes",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] >= 3
        assert len(data["items"]) >= 3
    
    async def test_get_note_by_id(
        self,
        client: AsyncClient,
        auth_headers: dict,
        cleanup_notes
    ):
        """Test getting specific note by ID"""
        # Create note
        create_response = await client.post(
            "/api/v1/notes",
            json={
                "title": "Specific Note",
                "content": "Specific content"
            },
            headers=auth_headers
        )
        note_id = create_response.json()["id"]
        
        response = await client.get(
            f"/api/v1/notes/{note_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == note_id
        assert data["title"] == "Specific Note"
    
    async def test_get_nonexistent_note(
        self,
        client: AsyncClient,
        auth_headers: dict,
        cleanup_notes
    ):
        """Test getting non-existent note"""
        response = await client.get(
            "/api/v1/notes/nonexistent-id",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_get_notes_with_tags_filter(
        self,
        client: AsyncClient,
        auth_headers: dict,
        cleanup_notes
    ):
        """Test filtering notes by tags"""
        # Create notes with different tags
        await client.post(
            "/api/v1/notes",
            json={
                "title": "Work Note",
                "content": "Work content",
                "tags": ["work"]
            },
            headers=auth_headers
        )
        
        await client.post(
            "/api/v1/notes",
            json={
                "title": "Personal Note",
                "content": "Personal content",
                "tags": ["personal"]
            },
            headers=auth_headers
        )
        
        response = await client.get(
            "/api/v1/notes?tags=work",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1


@pytest.mark.asyncio
class TestNoteUpdate:
    """Test note update endpoints"""
    
    async def test_update_note(
        self,
        client: AsyncClient,
        auth_headers: dict,
        cleanup_notes
    ):
        """Test updating a note"""
        # Create note
        create_response = await client.post(
            "/api/v1/notes",
            json={
                "title": "Original Title",
                "content": "Original content"
            },
            headers=auth_headers
        )
        note_id = create_response.json()["id"]
        
        # Update note
        response = await client.patch(
            f"/api/v1/notes/{note_id}",
            json={"title": "Updated Title"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["content"] == "Original content"
    
    async def test_update_note_content_creates_version(
        self,
        client: AsyncClient,
        auth_headers: dict,
        cleanup_notes
    ):
        """Test that updating content creates version history"""
        # Create note
        create_response = await client.post(
            "/api/v1/notes",
            json={
                "title": "Version Test",
                "content": "Original content"
            },
            headers=auth_headers
        )
        note_id = create_response.json()["id"]
        
        # Update content
        await client.patch(
            f"/api/v1/notes/{note_id}",
            json={"content": "Updated content"},
            headers=auth_headers
        )
        
        # Check versions
        response = await client.get(
            f"/api/v1/notes/{note_id}/versions",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        versions = response.json()
        assert len(versions) >= 1
        assert versions[0]["content"] == "Original content"
    
    async def test_pin_note(
        self,
        client: AsyncClient,
        auth_headers: dict,
        cleanup_notes
    ):
        """Test pinning a note"""
        # Create note
        create_response = await client.post(
            "/api/v1/notes",
            json={
                "title": "Pin Test",
                "content": "Content"
            },
            headers=auth_headers
        )
        note_id = create_response.json()["id"]
        
        # Pin note
        response = await client.patch(
            f"/api/v1/notes/{note_id}",
            json={"is_pinned": True},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_pinned"] is True
    
    async def test_archive_note(
        self,
        client: AsyncClient,
        auth_headers: dict,
        cleanup_notes
    ):
        """Test archiving a note"""
        # Create note
        create_response = await client.post(
            "/api/v1/notes",
            json={
                "title": "Archive Test",
                "content": "Content"
            },
            headers=auth_headers
        )
        note_id = create_response.json()["id"]
        
        # Archive note
        response = await client.patch(
            f"/api/v1/notes/{note_id}",
            json={"is_archived": True},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_archived"] is True


@pytest.mark.asyncio
class TestNoteDeletion:
    """Test note deletion endpoints"""
    
    async def test_delete_note(
        self,
        client: AsyncClient,
        auth_headers: dict,
        cleanup_notes
    ):
        """Test deleting a note"""
        # Create note
        create_response = await client.post(
            "/api/v1/notes",
            json={
                "title": "Delete Test",
                "content": "Content"
            },
            headers=auth_headers
        )
        note_id = create_response.json()["id"]
        
        # Delete note
        response = await client.delete(
            f"/api/v1/notes/{note_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify note is deleted
        get_response = await client.get(
            f"/api/v1/notes/{note_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404


@pytest.mark.asyncio
class TestNoteSearch:
    """Test note search functionality"""
    
    async def test_search_notes(
        self,
        client: AsyncClient,
        auth_headers: dict,
        cleanup_notes
    ):
        """Test full-text search for notes"""
        # Create notes with searchable content
        await client.post(
            "/api/v1/notes",
            json={
                "title": "Python Tutorial",
                "content": "Learn Python programming basics"
            },
            headers=auth_headers
        )
        
        await client.post(
            "/api/v1/notes",
            json={
                "title": "JavaScript Guide",
                "content": "JavaScript fundamentals"
            },
            headers=auth_headers
        )
        
        # Search for Python
        response = await client.get(
            "/api/v1/notes/search?q=Python",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert data["query"] == "Python"
        
        # Check that results contain Python
        found = False
        for item in data["items"]:
            if "Python" in item["title"] or "Python" in item["content"]:
                found = True
                break
        assert found


@pytest.mark.asyncio
class TestNoteLinks:
    """Test note linking functionality"""
    
    async def test_get_note_links(
        self,
        client: AsyncClient,
        auth_headers: dict,
        cleanup_notes
    ):
        """Test getting linked entities"""
        # Create note with links
        create_response = await client.post(
            "/api/v1/notes",
            json={
                "title": "Linked Note",
                "content": "Content",
                "linked_tasks": ["task-1", "task-2"]
            },
            headers=auth_headers
        )
        note_id = create_response.json()["id"]
        
        # Get links
        response = await client.get(
            f"/api/v1/notes/{note_id}/links",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "notes" in data
        assert len(data["tasks"]) == 2


@pytest.mark.asyncio
class TestMarkdownRendering:
    """Test markdown rendering"""
    
    async def test_render_markdown(
        self,
        client: AsyncClient,
        auth_headers: dict,
        cleanup_notes
    ):
        """Test rendering markdown to HTML"""
        # Create note with markdown
        create_response = await client.post(
            "/api/v1/notes",
            json={
                "title": "Markdown Test",
                "content": "# Heading\n\n**Bold text**\n\n- List item"
            },
            headers=auth_headers
        )
        note_id = create_response.json()["id"]
        
        # Render markdown
        response = await client.post(
            f"/api/v1/notes/{note_id}/render",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "html" in data
        assert "<h1>" in data["html"]
        assert "<strong>" in data["html"] or "<b>" in data["html"]
