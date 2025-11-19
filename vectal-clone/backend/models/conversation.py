"""
Conversation MongoDB models
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


class Message(BaseModel):
    """Chat message"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    tokens: Optional[int] = None
    mentions: List[str] = Field(default_factory=list)  # @task-id, @note-id
    commands: List[str] = Field(default_factory=list)  # /command
    
    # Task extraction
    extracted_tasks: List[Dict[str, Any]] = Field(default_factory=list)


class Conversation(BaseModel):
    """Conversation document model for MongoDB"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    
    # Messages
    messages: List[Message] = Field(default_factory=list)
    
    # Metadata
    title: Optional[str] = None  # Auto-generated from first message
    model: str = "gpt-4"
    total_tokens: int = 0
    
    # Status
    is_archived: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440001",
                "messages": [
                    {
                        "id": "msg-1",
                        "role": "user",
                        "content": "Create a task to review the project proposal",
                        "timestamp": "2024-01-01T12:00:00Z"
                    }
                ],
                "title": "Project Review Task",
                "model": "gpt-4",
                "total_tokens": 150
            }
        }
