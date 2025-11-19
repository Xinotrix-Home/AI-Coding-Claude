"""
Chat API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import Optional
import math
import uuid

from models.schemas.chat import (
    MessageCreate,
    ChatResponse,
    ConversationResponse,
    ConversationDetailResponse,
    ConversationListResponse,
    MessageResponse
)
from services.chat_service import ChatService
from api.dependencies.auth import get_current_user
from models.user import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def send_message(
    message_data: MessageCreate,
    stream: bool = False,
    current_user: User = Depends(get_current_user)
):
    """Send a chat message and get AI response"""
    try:
        conversation_id = message_data.conversation_id or str(uuid.uuid4())
        
        if stream:
            # Return streaming response
            async def generate():
                async for chunk in await ChatService.send_message(
                    conversation_id,
                    str(current_user.id),
                    message_data.content,
                    stream=True
                ):
                    yield chunk
            
            return StreamingResponse(generate(), media_type="text/event-stream")
        else:
            # Return complete response
            result = await ChatService.send_message(
                conversation_id,
                str(current_user.id),
                message_data.content,
                stream=False
            )
            
            return ChatResponse(**result)
            
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )


@router.get("/conversations", response_model=ConversationListResponse)
async def get_conversations(
    is_archived: bool = False,
    page: int = 1,
    page_size: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get user's conversations"""
    try:
        conversations, total = await ChatService.get_conversations(
            str(current_user.id),
            is_archived,
            page,
            page_size
        )
        
        # Convert to response
        conv_responses = []
        for conv in conversations:
            response = ConversationResponse(
                **conv.model_dump(),
                message_count=len(conv.messages)
            )
            conv_responses.append(response)
        
        total_pages = math.ceil(total / page_size)
        
        return ConversationListResponse(
            items=conv_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversations"
        )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific conversation with messages"""
    conversation = await ChatService.get_conversation(
        conversation_id,
        str(current_user.id)
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Convert messages
    messages = [MessageResponse(**msg.model_dump()) for msg in conversation.messages]
    
    response = ConversationDetailResponse(
        **conversation.model_dump(),
        message_count=len(conversation.messages),
        messages=messages
    )
    
    return response


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a conversation"""
    success = await ChatService.delete_conversation(
        conversation_id,
        str(current_user.id)
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return None
