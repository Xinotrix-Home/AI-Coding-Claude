"""
Integration tests for project management
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.user import User
from models.task import Project, ProjectCollaborator


@pytest.mark.asyncio
class TestProjectCreation:
    """Test project creation endpoints"""
    
    async def test_create_project_success(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """Test successful project creation"""
        response = await client.post(
            "/api/v1/projects",
            json={
                "name": "Test Project",
                "description": "Test Description",
                "color": "#3B82F6"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == "Test Project"
        assert data["description"] == "Test Description"
        assert data["color"] == "#3B82F6"
        assert data["is_archived"] is False
        assert "id" in data
    
    async def test_create_project_minimal(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test creating project with minimal data"""
        response = await client.post(
            "/api/v1/projects",
            json={"name": "Minimal Project"},
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Project"
    
    async def test_create_project_with_parent(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test creating project with parent"""
        import uuid
        
        # Create parent project
        parent = Project(
            id=uuid.uuid4(),
            user_id=test_user.id,
            name="Parent Project"
        )
        db_session.add(parent)
        
        # Add user as collaborator
        collab = ProjectCollaborator(
            project_id=parent.id,
            user_id=test_user.id,
            role='owner',
            status='accepted'
        )
        db_session.add(collab)
        await db_session.commit()
        
        response = await client.post(
            "/api/v1/projects",
            json={
                "name": "Child Project",
                "parent_project_id": str(parent.id)
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["parent_project_id"] == str(parent.id)
    
    async def test_create_project_without_auth(self, client: AsyncClient):
        """Test creating project without authentication"""
        response = await client.post(
            "/api/v1/projects",
            json={"name": "Test Project"}
        )
        
        assert response.status_code == 403


@pytest.mark.asyncio
class TestProjectRetrieval:
    """Test project retrieval endpoints"""
    
    async def test_get_all_projects(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test getting all projects"""
        import uuid
        
        # Create test projects
        for i in range(3):
            project = Project(
                id=uuid.uuid4(),
                user_id=test_user.id,
                name=f"Project {i}"
            )
            db_session.add(project)
            await db_session.flush()
            
            collab = ProjectCollaborator(
                project_id=project.id,
                user_id=test_user.id,
                role='owner',
                status='accepted'
            )
            db_session.add(collab)
        
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/projects",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] >= 3
        assert len(data["items"]) >= 3
    
    async def test_get_project_by_id(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test getting specific project by ID"""
        import uuid
        
        project = Project(
            id=uuid.uuid4(),
            user_id=test_user.id,
            name="Specific Project"
        )
        db_session.add(project)
        await db_session.flush()
        
        collab = ProjectCollaborator(
            project_id=project.id,
            user_id=test_user.id,
            role='owner',
            status='accepted'
        )
        db_session.add(collab)
        await db_session.commit()
        
        response = await client.get(
            f"/api/v1/projects/{project.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(project.id)
        assert data["name"] == "Specific Project"
    
    async def test_get_nonexistent_project(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting non-existent project"""
        import uuid
        
        response = await client.get(
            f"/api/v1/projects/{uuid.uuid4()}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_get_archived_projects(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test getting archived projects"""
        import uuid
        
        # Create archived project
        project = Project(
            id=uuid.uuid4(),
            user_id=test_user.id,
            name="Archived Project",
            is_archived=True
        )
        db_session.add(project)
        await db_session.flush()
        
        collab = ProjectCollaborator(
            project_id=project.id,
            user_id=test_user.id,
            role='owner',
            status='accepted'
        )
        db_session.add(collab)
        await db_session.commit()
        
        # Should not appear in default list
        response = await client.get(
            "/api/v1/projects",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Should appear when including archived
        response = await client.get(
            "/api/v1/projects?include_archived=true",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        archived_names = [p["name"] for p in data["items"]]
        assert "Archived Project" in archived_names


@pytest.mark.asyncio
class TestProjectUpdate:
    """Test project update endpoints"""
    
    async def test_update_project(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test updating a project"""
        import uuid
        
        project = Project(
            id=uuid.uuid4(),
            user_id=test_user.id,
            name="Original Name"
        )
        db_session.add(project)
        await db_session.flush()
        
        collab = ProjectCollaborator(
            project_id=project.id,
            user_id=test_user.id,
            role='owner',
            status='accepted'
        )
        db_session.add(collab)
        await db_session.commit()
        
        response = await client.patch(
            f"/api/v1/projects/{project.id}",
            json={"name": "Updated Name"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
    
    async def test_archive_project(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test archiving a project"""
        import uuid
        
        project = Project(
            id=uuid.uuid4(),
            user_id=test_user.id,
            name="Project to Archive"
        )
        db_session.add(project)
        await db_session.flush()
        
        collab = ProjectCollaborator(
            project_id=project.id,
            user_id=test_user.id,
            role='owner',
            status='accepted'
        )
        db_session.add(collab)
        await db_session.commit()
        
        response = await client.post(
            f"/api/v1/projects/{project.id}/archive",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_archived"] is True
    
    async def test_unarchive_project(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test unarchiving a project"""
        import uuid
        
        project = Project(
            id=uuid.uuid4(),
            user_id=test_user.id,
            name="Archived Project",
            is_archived=True
        )
        db_session.add(project)
        await db_session.flush()
        
        collab = ProjectCollaborator(
            project_id=project.id,
            user_id=test_user.id,
            role='owner',
            status='accepted'
        )
        db_session.add(collab)
        await db_session.commit()
        
        response = await client.post(
            f"/api/v1/projects/{project.id}/unarchive",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_archived"] is False


@pytest.mark.asyncio
class TestProjectDeletion:
    """Test project deletion endpoints"""
    
    async def test_delete_project(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test deleting a project"""
        import uuid
        
        project = Project(
            id=uuid.uuid4(),
            user_id=test_user.id,
            name="Project to Delete"
        )
        db_session.add(project)
        await db_session.flush()
        
        collab = ProjectCollaborator(
            project_id=project.id,
            user_id=test_user.id,
            role='owner',
            status='accepted'
        )
        db_session.add(collab)
        await db_session.commit()
        project_id = project.id
        
        response = await client.delete(
            f"/api/v1/projects/{project_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify project is deleted
        result = await db_session.execute(
            select(Project).where(Project.id == project_id)
        )
        deleted_project = result.scalar_one_or_none()
        assert deleted_project is None


@pytest.mark.asyncio
class TestProjectProgress:
    """Test project progress endpoints"""
    
    async def test_get_project_progress(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test getting project progress"""
        import uuid
        from models.task import Task
        
        project = Project(
            id=uuid.uuid4(),
            user_id=test_user.id,
            name="Progress Project"
        )
        db_session.add(project)
        await db_session.flush()
        
        collab = ProjectCollaborator(
            project_id=project.id,
            user_id=test_user.id,
            role='owner',
            status='accepted'
        )
        db_session.add(collab)
        
        # Add tasks
        for i in range(5):
            task = Task(
                id=uuid.uuid4(),
                user_id=test_user.id,
                project_id=project.id,
                title=f"Task {i}",
                status='completed' if i < 2 else 'pending'
            )
            db_session.add(task)
        
        await db_session.commit()
        
        response = await client.get(
            f"/api/v1/projects/{project.id}/progress",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_tasks"] == 5
        assert data["completed_tasks"] == 2
        assert data["progress_percentage"] == 40.0


@pytest.mark.asyncio
class TestProjectCollaboration:
    """Test project collaboration endpoints"""
    
    async def test_add_collaborator(
        self,
        client: AsyncClient,
        test_user: User,
        test_user_unverified: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test adding a collaborator"""
        import uuid
        
        project = Project(
            id=uuid.uuid4(),
            user_id=test_user.id,
            name="Collaborative Project"
        )
        db_session.add(project)
        await db_session.flush()
        
        collab = ProjectCollaborator(
            project_id=project.id,
            user_id=test_user.id,
            role='owner',
            status='accepted'
        )
        db_session.add(collab)
        await db_session.commit()
        
        response = await client.post(
            f"/api/v1/projects/{project.id}/share",
            json={
                "user_email": test_user_unverified.email,
                "role": "editor"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "editor"
        assert data["status"] == "pending"
    
    async def test_get_collaborators(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test getting project collaborators"""
        import uuid
        
        project = Project(
            id=uuid.uuid4(),
            user_id=test_user.id,
            name="Project with Collaborators"
        )
        db_session.add(project)
        await db_session.flush()
        
        collab = ProjectCollaborator(
            project_id=project.id,
            user_id=test_user.id,
            role='owner',
            status='accepted'
        )
        db_session.add(collab)
        await db_session.commit()
        
        response = await client.get(
            f"/api/v1/projects/{project.id}/collaborators",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["role"] == "owner"
