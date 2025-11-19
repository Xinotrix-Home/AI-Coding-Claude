"""
Integration tests for authentication security features
"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch
import asyncio

from models.user import User


@pytest.mark.asyncio
class TestRateLimiting:
    """Test rate limiting functionality"""
    
    async def test_login_rate_limit(self, client: AsyncClient, test_user: User):
        """Test rate limiting on login endpoint"""
        # Make multiple failed login attempts
        for i in range(6):
            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "WrongPassword123!@#"
                }
            )
            
            if i < 5:
                # First 5 attempts should be allowed
                assert response.status_code == 401
            else:
                # 6th attempt should be rate limited
                assert response.status_code == 429
                assert "Rate limit exceeded" in str(response.json())


@pytest.mark.asyncio
class TestAccountLockout:
    """Test account lockout after failed attempts"""
    
    @patch('utils.account_security.AccountSecurity.record_failed_login')
    @patch('utils.account_security.AccountSecurity.is_account_locked')
    async def test_account_lockout_after_failed_attempts(
        self,
        mock_is_locked,
        mock_record,
        client: AsyncClient,
        test_user: User
    ):
        """Test account lockout after multiple failed login attempts"""
        # Simulate account being locked
        mock_is_locked.return_value = True
        mock_record.return_value = 10
        
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword123!@#"
            }
        )
        
        assert response.status_code == 403
        assert "locked" in response.json()["detail"].lower()
    
    @patch('utils.account_security.AccountSecurity.clear_failed_attempts')
    @patch('utils.account_security.AccountSecurity.is_account_locked')
    async def test_clear_failed_attempts_on_success(
        self,
        mock_is_locked,
        mock_clear,
        client: AsyncClient,
        test_user: User
    ):
        """Test that failed attempts are cleared on successful login"""
        mock_is_locked.return_value = False
        
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "Test123!@#"
            }
        )
        
        assert response.status_code == 200
        # Verify clear_failed_attempts was called
        mock_clear.assert_called_once()


@pytest.mark.asyncio
class TestPasswordSecurity:
    """Test password security requirements"""
    
    async def test_password_not_returned_in_response(self, client: AsyncClient):
        """Test that password is never returned in API responses"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "security@example.com",
                "password": "Test123!@#",
                "full_name": "Security Test"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Ensure password fields are not in response
        assert "password" not in data
        assert "password_hash" not in data
    
    async def test_password_hash_stored(self, client: AsyncClient, db_session):
        """Test that password is hashed before storage"""
        from sqlalchemy import select
        from models.user import User
        
        password = "Test123!@#"
        
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "hashtest@example.com",
                "password": password
            }
        )
        
        assert response.status_code == 201
        
        # Get user from database
        result = await db_session.execute(
            select(User).where(User.email == "hashtest@example.com")
        )
        user = result.scalar_one_or_none()
        
        # Verify password is hashed
        assert user.password_hash is not None
        assert user.password_hash != password
        assert len(user.password_hash) > 50  # Bcrypt hashes are long


@pytest.mark.asyncio
class TestTokenSecurity:
    """Test JWT token security"""
    
    async def test_expired_token_rejected(self, client: AsyncClient, test_user: User):
        """Test that expired tokens are rejected"""
        from utils.jwt import create_access_token
        from datetime import timedelta
        
        # Create token that expires immediately
        expired_token = create_access_token(
            {"sub": str(test_user.id)},
            expires_delta=timedelta(seconds=-1)
        )
        
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401
    
    async def test_malformed_token_rejected(self, client: AsyncClient):
        """Test that malformed tokens are rejected"""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer malformed.token"}
        )
        
        assert response.status_code == 401
    
    async def test_missing_bearer_prefix(self, client: AsyncClient, test_user: User):
        """Test that tokens without Bearer prefix are rejected"""
        from utils.jwt import create_access_token
        
        token = create_access_token({"sub": str(test_user.id)})
        
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": token}  # Missing "Bearer " prefix
        )
        
        assert response.status_code == 403


@pytest.mark.asyncio
class TestInactiveUser:
    """Test inactive user handling"""
    
    async def test_inactive_user_cannot_login(self, client: AsyncClient, db_session):
        """Test that inactive users cannot login"""
        from models.user import User
        from utils.password import hash_password
        import uuid
        
        # Create inactive user
        inactive_user = User(
            id=uuid.uuid4(),
            email="inactive@example.com",
            password_hash=hash_password("Test123!@#"),
            is_active=False,
            is_verified=True
        )
        db_session.add(inactive_user)
        await db_session.commit()
        
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "inactive@example.com",
                "password": "Test123!@#"
            }
        )
        
        assert response.status_code == 401
        assert "disabled" in response.json()["detail"].lower()
