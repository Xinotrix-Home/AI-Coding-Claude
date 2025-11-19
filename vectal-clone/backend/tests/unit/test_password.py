"""
Unit tests for password utilities
"""
import pytest
from utils.password import (
    hash_password,
    verify_password,
    validate_password_strength,
    validate_email
)


class TestPasswordHashing:
    """Test password hashing and verification"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "Test123!@#"
        hashed = hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "Test123!@#"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "Test123!@#"
        wrong_password = "Wrong123!@#"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_hash_different_for_same_password(self):
        """Test that same password produces different hashes (salt)"""
        password = "Test123!@#"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestPasswordValidation:
    """Test password strength validation"""
    
    def test_valid_password(self):
        """Test valid password"""
        is_valid, msg = validate_password_strength("Test123!@#")
        assert is_valid is True
        assert msg == ""
    
    def test_password_too_short(self):
        """Test password too short"""
        is_valid, msg = validate_password_strength("Test1!")
        assert is_valid is False
        assert "at least 8 characters" in msg
    
    def test_password_no_lowercase(self):
        """Test password without lowercase"""
        is_valid, msg = validate_password_strength("TEST123!@#")
        assert is_valid is False
        assert "lowercase" in msg
    
    def test_password_no_uppercase(self):
        """Test password without uppercase"""
        is_valid, msg = validate_password_strength("test123!@#")
        assert is_valid is False
        assert "uppercase" in msg
    
    def test_password_no_digit(self):
        """Test password without digit"""
        is_valid, msg = validate_password_strength("TestTest!@#")
        assert is_valid is False
        assert "digit" in msg
    
    def test_password_no_special_char(self):
        """Test password without special character"""
        is_valid, msg = validate_password_strength("Test12345")
        assert is_valid is False
        assert "special character" in msg


class TestEmailValidation:
    """Test email validation"""
    
    def test_valid_email(self):
        """Test valid email addresses"""
        assert validate_email("test@example.com") is True
        assert validate_email("user.name@example.co.uk") is True
        assert validate_email("user+tag@example.com") is True
    
    def test_invalid_email(self):
        """Test invalid email addresses"""
        assert validate_email("invalid") is False
        assert validate_email("@example.com") is False
        assert validate_email("user@") is False
        assert validate_email("user@.com") is False
