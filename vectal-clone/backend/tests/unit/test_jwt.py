"""
Unit tests for JWT utilities
"""
import pytest
from datetime import timedelta
from utils.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_access_token,
    verify_refresh_token
)


class TestJWTTokens:
    """Test JWT token creation and verification"""
    
    def test_create_access_token(self):
        """Test access token creation"""
        data = {"sub": "user123"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        data = {"sub": "user123"}
        token = create_refresh_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_token(self):
        """Test token decoding"""
        data = {"sub": "user123"}
        token = create_access_token(data)
        
        payload = decode_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user123"
        assert "exp" in payload
        assert "type" in payload
    
    def test_verify_access_token(self):
        """Test access token verification"""
        data = {"sub": "user123"}
        token = create_access_token(data)
        
        payload = verify_access_token(token)
        
        assert payload["sub"] == "user123"
        assert payload["type"] == "access"
    
    def test_verify_refresh_token(self):
        """Test refresh token verification"""
        data = {"sub": "user123"}
        token = create_refresh_token(data)
        
        payload = verify_refresh_token(token)
        
        assert payload["sub"] == "user123"
        assert payload["type"] == "refresh"
    
    def test_verify_wrong_token_type(self):
        """Test verifying token with wrong type"""
        data = {"sub": "user123"}
        access_token = create_access_token(data)
        
        with pytest.raises(ValueError, match="Invalid token type"):
            verify_refresh_token(access_token)
    
    def test_decode_invalid_token(self):
        """Test decoding invalid token"""
        with pytest.raises(ValueError, match="Invalid token"):
            decode_token("invalid.token.here")
    
    def test_token_expiry(self):
        """Test token with custom expiry"""
        data = {"sub": "user123"}
        token = create_access_token(data, expires_delta=timedelta(seconds=1))
        
        payload = decode_token(token)
        assert "exp" in payload
        
        # Token should be valid immediately
        verify_access_token(token)
