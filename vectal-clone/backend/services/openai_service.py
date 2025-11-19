"""
OpenAI service for GPT-4 integration
"""
from openai import AsyncOpenAI
from typing import List, Dict, AsyncGenerator
import logging

from utils.config import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class OpenAIService:
    """OpenAI service for chat completions"""
    
    @staticmethod
    async def create_chat_completion(
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ):
        """Create a chat completion"""
        try:
            response = await openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            return response
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    @staticmethod
    async def create_streaming_completion(
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> AsyncGenerator[str, None]:
        """Create a streaming chat completion"""
        try:
            stream = await openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise
    
    @staticmethod
    async def create_embedding(text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """Create text embedding"""
        try:
            response = await openai_client.embeddings.create(
                model=model,
                input=text
            )
            
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise
    
    @staticmethod
    def count_tokens(text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4
    
    @staticmethod
    def build_system_prompt() -> str:
        """Build system prompt for the AI assistant"""
        return """You are a helpful AI productivity assistant. You help users manage their tasks, notes, and projects.

Your capabilities:
- Create, update, and organize tasks
- Take and organize notes
- Manage projects
- Answer questions about productivity
- Provide suggestions and insights

When users ask you to create tasks, extract the relevant details (title, description, due date, priority) and confirm before creating.

Be concise, helpful, and proactive in suggesting ways to improve productivity."""
