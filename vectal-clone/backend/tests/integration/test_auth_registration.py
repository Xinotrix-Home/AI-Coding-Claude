"""
Integration tests for user registration
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.user import User


@pytest.mark.asyncio
class TestUserRegistration:
    """Test user registration endpoints"""
    
    async def test_register_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test successful user registration"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "Test123!@#",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data
        
        # Verify user in database
        result = await db_session.execute(
            select(User).where(User.email == "newuser@example.com")
        )
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.email == "newuser@example.com"
    
    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User):
        """Test registration with duplicate email"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "password": "Test123!@#"
            }
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "Test123!@#"
            }
        )
        
        assert response.status_code == 422
    
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "weak"
            }
        )
        
        assert response.status_code == 422
    
    async def test_register_no_uppercase(self, client: AsyncClient):
        """Test registration with password missing uppercase"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "test123!@#"
            }
        )
        
        assert response.status_code == 422
    
    async def test_register_no_special_char(self, client: AsyncClient):
        """Test registration with password missing special character"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "Test12345"
            }
        )
        
        assert response.status_code == 422
    
    async def test_register_without_full_name(self, client: AsyncClient):
        """Test registration without full name (optional field)"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "Test123!@#"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] is None
