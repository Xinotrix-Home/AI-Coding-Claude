"""
Integration tests for task management
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from models.user import User
from models.task import Task


@pytest.mark.asyncio
class TestTaskCreation:
    """Test task creation endpoints"""
    
    async def test_create_task_success(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """Test successful task creation"""
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Test Task",
                "description": "Test Description",
                "priority": 2
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["title"] == "Test Task"
        assert data["description"] == "Test Description"
        assert data["priority"] == 2
        assert data["status"] == "pending"
        assert "id" in data
    
    async def test_create_task_with_due_date(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test creating task with due date"""
        due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Task with due date",
                "due_date": due_date
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["due_date"] is not None
    
    async def test_create_task_with_labels(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test creating task with labels"""
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Task with labels",
                "labels": ["work", "urgent"]
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "work" in data["labels"]
        assert "urgent" in data["labels"]
    
    async def test_create_task_without_auth(self, client: AsyncClient):
        """Test creating task without authentication"""
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Task"}
        )
        
        assert response.status_code == 403
    
    async def test_create_task_invalid_priority(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test creating task with invalid priority"""
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Test Task",
                "priority": 10  # Invalid, should be 0-4
            },
            headers=auth_headers
        )
        
        assert response.status_code == 422


@pytest.mark.asyncio
class TestTaskRetrieval:
    """Test task retrieval endpoints"""
    
    async def test_get_all_tasks(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test getting all tasks"""
        # Create test tasks
        import uuid
        for i in range(3):
            task = Task(
                id=uuid.uuid4(),
                user_id=test_user.id,
                title=f"Task {i}",
                status="pending",
                priority=i
            )
            db_session.add(task)
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/tasks",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] == 3
        assert len(data["items"]) == 3
    
    async def test_get_tasks_with_status_filter(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test getting tasks with status filter"""
        import uuid
        
        # Create pending and completed tasks
        pending_task = Task(
            id=uuid.uuid4(),
            user_id=test_user.id,
            title="Pending Task",
            status="pending"
        )
        completed_task = Task(
            id=uuid.uuid4(),
            user_id=test_user.id,
            title="Completed Task",
            status="completed"
        )
        db_session.add_all([pending_task, completed_task])
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/tasks?status=pending",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] == 1
        assert data["items"][0]["status"] == "pending"
    
    async def test_get_task_by_id(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test getting specific task by ID"""
        import uuid
        
        task = Task(
            id=uuid.uuid4(),
            user_id=test_user.id,
            title="Specific Task",
            status="pending"
        )
        db_session.add(task)
        await db_session.commit()
        
        response = await client.get(
            f"/api/v1/tasks/{task.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(task.id)
        assert data["title"] == "Specific Task"
    
    async def test_get_nonexistent_task(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting non-existent task"""
        import uuid
        
        response = await client.get(
            f"/api/v1/tasks/{uuid.uuid4()}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_get_today_tasks(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test getting tasks due today"""
        import uuid
        
        today = datetime.utcnow().replace(hour=12, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        today_task = Task(
            id=uuid.uuid4(),
            user_id=test_user.id,
            title="Today Task",
            status="pending",
            due_date=today
        )
        tomorrow_task = Task(
            id=uuid.uuid4(),
            user_id=test_user.id,
            title="Tomorrow Task",
            status="pending",
            due_date=tomorrow
        )
        db_session.add_all([today_task, tomorrow_task])
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/tasks/today",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only return today's task
        assert data["total"] >= 1
        task_titles = [item["title"] for item in data["items"]]
        assert "Today Task" in task_titles


@pytest.mark.asyncio
class TestTaskUpdate:
    """Test task update endpoints"""
    
    async def test_update_task(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test updating a task"""
        import uuid
        
        task = Task(
            id=uuid.uuid4(),
            user_id=test_user.id,
            title="Original Title",
            status="pending"
        )
        db_session.add(task)
        await db_session.commit()
        
        response = await client.patch(
            f"/api/v1/tasks/{task.id}",
            json={"title": "Updated Title"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
    
    async def test_update_task_priority(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test updating task priority"""
        import uuid
        
        task = Task(
            id=uuid.uuid4(),
            user_id=test_user.id,
            title="Task",
            priority=0
        )
        db_session.add(task)
        await db_session.commit()
        
        response = await client.patch(
            f"/api/v1/tasks/{task.id}",
            json={"priority": 3},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == 3


@pytest.mark.asyncio
class TestTaskCompletion:
    """Test task completion endpoints"""
    
    async def test_complete_task(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test marking task as completed"""
        import uuid
        
        task = Task(
            id=uuid.uuid4(),
            user_id=test_user.id,
            title="Task to Complete",
            status="pending"
        )
        db_session.add(task)
        await db_session.commit()
        
        response = await client.post(
            f"/api/v1/tasks/{task.id}/complete",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None
    
    async def test_uncomplete_task(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test marking task as incomplete"""
        import uuid
        
        task = Task(
            id=uuid.uuid4(),
            user_id=test_user.id,
            title="Completed Task",
            status="completed",
            completed_at=datetime.utcnow()
        )
        db_session.add(task)
        await db_session.commit()
        
        response = await client.post(
            f"/api/v1/tasks/{task.id}/uncomplete",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert data["completed_at"] is None


@pytest.mark.asyncio
class TestTaskDeletion:
    """Test task deletion endpoints"""
    
    async def test_delete_task(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test deleting a task"""
        import uuid
        
        task = Task(
            id=uuid.uuid4(),
            user_id=test_user.id,
            title="Task to Delete",
            status="pending"
        )
        db_session.add(task)
        await db_session.commit()
        task_id = task.id
        
        response = await client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify task is deleted
        result = await db_session.execute(
            select(Task).where(Task.id == task_id)
        )
        deleted_task = result.scalar_one_or_none()
        assert deleted_task is None


@pytest.mark.asyncio
class TestTaskRecurrence:
    """Test task recurrence endpoints"""
    
    async def test_set_task_recurrence(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test setting recurrence rule for task"""
        import uuid
        
        task = Task(
            id=uuid.uuid4(),
            user_id=test_user.id,
            title="Recurring Task",
            status="pending"
        )
        db_session.add(task)
        await db_session.commit()
        
        response = await client.post(
            f"/api/v1/tasks/{task.id}/recurrence?frequency=daily&interval=1",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["recurrence_rule"] is not None
        assert "DAILY" in data["recurrence_rule"]
    
    async def test_remove_task_recurrence(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test removing recurrence rule from task"""
        import uuid
        
        task = Task(
            id=uuid.uuid4(),
            user_id=test_user.id,
            title="Recurring Task",
            status="pending",
            recurrence_rule="FREQ=DAILY;INTERVAL=1"
        )
        db_session.add(task)
        await db_session.commit()
        
        response = await client.delete(
            f"/api/v1/tasks/{task.id}/recurrence",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["recurrence_rule"] is None
