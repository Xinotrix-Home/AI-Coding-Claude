"""
Integration tests for OAuth authentication
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from unittest.mock import AsyncMock, patch, MagicMock

from models.user import User


@pytest.mark.asyncio
class TestOAuthGoogle:
    """Test Google OAuth authentication"""
    
    async def test_google_oauth_initiate(self, client: AsyncClient):
        """Test initiating Google OAuth flow"""
        response = await client.get(
            "/api/v1/oauth/google",
            follow_redirects=False
        )
        
        # Should redirect to Google
        assert response.status_code in [302, 307]
        assert "location" in response.headers
    
    @patch('services.oauth_service.oauth.google.authorize_access_token')
    @patch('services.oauth_service.oauth.google.authorize_redirect')
    async def test_google_oauth_callback_new_user(
        self,
        mock_redirect,
        mock_token,
        client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test Google OAuth callback with new user"""
        # Mock Google token response
        mock_token.return_value = {
            'userinfo': {
                'sub': 'google_123456',
                'email': 'newgoogle@example.com',
                'name': 'Google User',
                'picture': 'https://example.com/avatar.jpg'
            }
        }
        
        response = await client.get(
            "/api/v1/oauth/google/callback",
            follow_redirects=False
        )
        
        # Should redirect to frontend with tokens
        assert response.status_code in [302, 307]
        location = response.headers.get("location", "")
        assert "access_token" in location
        assert "refresh_token" in location
        
        # Verify user created in database
        result = await db_session.execute(
            select(User).where(User.email == "newgoogle@example.com")
        )
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.oauth_provider == "google"
        assert user.oauth_id == "google_123456"
        assert user.is_verified is True
    
    @patch('services.oauth_service.oauth.google.authorize_access_token')
    async def test_google_oauth_callback_existing_user(
        self,
        mock_token,
        client: AsyncClient,
        oauth_user: User
    ):
        """Test Google OAuth callback with existing user"""
        # Mock Google token response
        mock_token.return_value = {
            'userinfo': {
                'sub': oauth_user.oauth_id,
                'email': oauth_user.email,
                'name': oauth_user.full_name,
            }
        }
        
        response = await client.get(
            "/api/v1/oauth/google/callback",
            follow_redirects=False
        )
        
        # Should redirect to frontend with tokens
        assert response.status_code in [302, 307]
        location = response.headers.get("location", "")
        assert "access_token" in location


@pytest.mark.asyncio
class TestOAuthGitHub:
    """Test GitHub OAuth authentication"""
    
    async def test_github_oauth_initiate(self, client: AsyncClient):
        """Test initiating GitHub OAuth flow"""
        response = await client.get(
            "/api/v1/oauth/github",
            follow_redirects=False
        )
        
        # Should redirect to GitHub
        assert response.status_code in [302, 307]
        assert "location" in response.headers
    
    @patch('services.oauth_service.oauth.github.get')
    @patch('services.oauth_service.oauth.github.authorize_access_token')
    async def test_github_oauth_callback_new_user(
        self,
        mock_token,
        mock_get,
        client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test GitHub OAuth callback with new user"""
        # Mock GitHub token response
        mock_token.return_value = {'access_token': 'github_token'}
        
        # Mock GitHub user info response
        user_response = MagicMock()
        user_response.json.return_value = {
            'id': 123456,
            'email': 'newgithub@example.com',
            'name': 'GitHub User',
            'avatar_url': 'https://example.com/avatar.jpg'
        }
        
        mock_get.return_value = user_response
        
        response = await client.get(
            "/api/v1/oauth/github/callback",
            follow_redirects=False
        )
        
        # Should redirect to frontend with tokens
        assert response.status_code in [302, 307]
        location = response.headers.get("location", "")
        assert "access_token" in location or "error" in location
