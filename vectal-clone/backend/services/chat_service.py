"""
Chat service layer
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List, Tuple, Dict, Any, AsyncGenerator
from datetime import datetime
import re
import json

from models.conversation import Conversation, Message
from services.openai_service import OpenAIService
from db.mongodb import get_collection, Collections
import logging

logger = logging.getLogger(__name__)


class ChatService:
    """Chat service"""
    
    @staticmethod
    async def create_conversation(user_id: str) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(user_id=user_id)
        
        collection = get_collection(Collections.CONVERSATIONS)
        await collection.insert_one(conversation.model_dump())
        
        # Create indexes
        await ChatService._ensure_indexes()
        
        logger.info(f"Conversation created: {conversation.id} for user {user_id}")
        return conversation
    
    @staticmethod
    async def get_conversation(
        conversation_id: str,
        user_id: str
    ) -> Optional[Conversation]:
        """Get a conversation by ID"""
        collection = get_collection(Collections.CONVERSATIONS)
        
        conv_dict = await collection.find_one({
            "id": conversation_id,
            "user_id": user_id
        })
        
        if conv_dict:
            return Conversation(**conv_dict)
        return None
    
    @staticmethod
    async def get_conversations(
        user_id: str,
        is_archived: bool = False,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[Conversation], int]:
        """Get conversations with pagination"""
        collection = get_collection(Collections.CONVERSATIONS)
        
        query = {
            "user_id": user_id,
            "is_archived": is_archived
        }
        
        # Get total count
        total = await collection.count_documents(query)
        
        # Get paginated results
        skip = (page - 1) * page_size
        cursor = collection.find(query).sort("updated_at", -1).skip(skip).limit(page_size)
        
        conversations = []
        async for conv_dict in cursor:
            conversations.append(Conversation(**conv_dict))
        
        return conversations, total
    
    @staticmethod
    async def send_message(
        conversation_id: str,
        user_id: str,
        content: str,
        stream: bool = False
    ):
        """Send a message and get AI response"""
        # Get or create conversation
        conversation = await ChatService.get_conversation(conversation_id, user_id)
        if not conversation:
            conversation = await ChatService.create_conversation(user_id)
            conversation.id = conversation_id
        
        # Parse mentions and commands
        mentions = ChatService._extract_mentions(content)
        commands = ChatService._extract_commands(content)
        
        # Create user message
        user_message = Message(
            role="user",
            content=content,
            mentions=mentions,
            commands=commands
        )
        
        conversation.messages.append(user_message)
        
        # Build messages for OpenAI
        openai_messages = ChatService._build_openai_messages(conversation)
        
        if stream:
            # Return streaming response
            return ChatService._stream_response(conversation, user_id, openai_messages)
        else:
            # Get complete response
            response = await OpenAIService.create_chat_completion(
                messages=openai_messages,
                model=conversation.model
            )
            
            assistant_content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Create assistant message
            assistant_message = Message(
                role="assistant",
                content=assistant_content,
                tokens=tokens_used
            )
            
            # Extract tasks if mentioned
            extracted_tasks = await ChatService._extract_tasks(assistant_content)
            if extracted_tasks:
                assistant_message.extracted_tasks = extracted_tasks
            
            conversation.messages.append(assistant_message)
            conversation.total_tokens += tokens_used
            conversation.updated_at = datetime.utcnow()
            conversation.last_message_at = datetime.utcnow()
            
            # Auto-generate title from first message
            if not conversation.title and len(conversation.messages) >= 2:
                conversation.title = ChatService._generate_title(content)
            
            # Save conversation
            await ChatService._save_conversation(conversation)
            
            return {
                "conversation_id": conversation.id,
                "message": assistant_message.model_dump(),
                "extracted_tasks": extracted_tasks
            }
    
    @staticmethod
    async def _stream_response(
        conversation: Conversation,
        user_id: str,
        openai_messages: List[Dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        """Stream AI response"""
        full_response = ""
        
        async for chunk in OpenAIService.create_streaming_completion(
            messages=openai_messages,
            model=conversation.model
        ):
            full_response += chunk
            yield chunk
        
        # After streaming complete, save the message
        assistant_message = Message(
            role="assistant",
            content=full_response
        )
        
        conversation.messages.append(assistant_message)
        conversation.updated_at = datetime.utcnow()
        conversation.last_message_at = datetime.utcnow()
        
        if not conversation.title and len(conversation.messages) >= 2:
            conversation.title = ChatService._generate_title(conversation.messages[0].content)
        
        await ChatService._save_conversation(conversation)
    
    @staticmethod
    async def delete_conversation(
        conversation_id: str,
        user_id: str
    ) -> bool:
        """Delete a conversation"""
        collection = get_collection(Collections.CONVERSATIONS)
        
        result = await collection.delete_one({
            "id": conversation_id,
            "user_id": user_id
        })
        
        if result.deleted_count > 0:
            logger.info(f"Conversation deleted: {conversation_id}")
            return True
        return False
    
    @staticmethod
    def _build_openai_messages(conversation: Conversation) -> List[Dict[str, str]]:
        """Build messages array for OpenAI API"""
        messages = [
            {"role": "system", "content": OpenAIService.build_system_prompt()}
        ]
        
        # Add conversation history (last 10 messages for context)
        for msg in conversation.messages[-10:]:
            if msg.role in ["user", "assistant"]:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        return messages
    
    @staticmethod
    def _extract_mentions(content: str) -> List[str]:
        """Extract @mentions from message"""
        # Pattern: @task-id or @note-id
        pattern = r'@([\w-]+)'
        mentions = re.findall(pattern, content)
        return mentions
    
    @staticmethod
    def _extract_commands(content: str) -> List[str]:
        """Extract /commands from message"""
        # Pattern: /command
        pattern = r'/([\w-]+)'
        commands = re.findall(pattern, content)
        return commands
    
    @staticmethod
    async def _extract_tasks(content: str) -> List[Dict[str, Any]]:
        """Extract task information from AI response"""
        # Simple pattern matching for task creation
        tasks = []
        
        # Look for task-like patterns
        task_patterns = [
            r"create.*task.*['\"](.+?)['\"]",
            r"add.*task.*['\"](.+?)['\"]",
            r"task:.*['\"](.+?)['\"]"
        ]
        
        for pattern in task_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                tasks.append({
                    "title": match,
                    "status": "pending"
                })
        
        return tasks
    
    @staticmethod
    def _generate_title(first_message: str) -> str:
        """Generate conversation title from first message"""
        # Take first 50 characters
        title = first_message[:50]
        if len(first_message) > 50:
            title += "..."
        return title
    
    @staticmethod
    async def _save_conversation(conversation: Conversation):
        """Save conversation to database"""
        collection = get_collection(Collections.CONVERSATIONS)
        
        await collection.update_one(
            {"id": conversation.id},
            {"$set": conversation.model_dump()},
            upsert=True
        )
    
    @staticmethod
    async def _ensure_indexes():
        """Ensure MongoDB indexes exist"""
        collection = get_collection(Collections.CONVERSATIONS)
        
        await collection.create_index("user_id")
        await collection.create_index("updated_at")
        await collection.create_index([("user_id", 1), ("is_archived", 1)])
