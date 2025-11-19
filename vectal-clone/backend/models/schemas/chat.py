"""
Chat Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class MessageCreate(BaseModel):
    """Message creation schema"""
    content: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None


class MessageResponse(BaseModel):
    """Message response schema"""
    id: str
    role: str
    content: str
    timestamp: datetime
    tokens: Optional[int] = None
    mentions: List[str] = []
    commands: List[str] = []
    extracted_tasks: List[Dict[str, Any]] = []


class ConversationResponse(BaseModel):
    """Conversation response schema"""
    id: str
    user_id: str
    title: Optional[str]
    model: str
    total_tokens: int
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime]
    message_count: int = 0


class ConversationDetailResponse(ConversationResponse):
    """Conversation with messages"""
    messages: List[MessageResponse]


class ConversationListResponse(BaseModel):
    """Paginated conversation list"""
    items: List[ConversationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ChatResponse(BaseModel):
    """Chat message response"""
    conversation_id: str
    message: MessageResponse
    extracted_tasks: List[Dict[str, Any]] = []
