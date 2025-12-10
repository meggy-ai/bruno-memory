"""Base backend implementation for bruno-memory."""

import json
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone

from bruno_core.interfaces import MemoryInterface
from bruno_core.models.message import Message, MessageRole
from bruno_core.models.context import ConversationContext, SessionContext, UserContext
from bruno_core.models.memory import MemoryEntry, MemoryQuery

from bruno_memory.base.memory_config import MemoryConfig
from bruno_memory.exceptions import (
    StorageError,
    RetrievalError,
    SessionError,
    ContextBuildingError,
    InvalidQueryError,
)


class BaseMemoryBackend(MemoryInterface, ABC):
    """Abstract base class for all memory backends.
    
    This class provides common functionality and defines the interface
    that all memory backends must implement. It handles message
    serialization, validation, and common utility methods.
    """
    
    def __init__(self, config: MemoryConfig):
        """Initialize the base backend.
        
        Args:
            config: Backend-specific configuration
        """
        self.config = config
        self._initialized = False
        self._closed = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the backend (create connections, tables, etc.)."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close backend connections and cleanup resources.""" 
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the backend is healthy and ready."""
        pass
    
    # Message Operations (Abstract - must be implemented by subclasses)
    
    @abstractmethod
    async def store_message(self, message: Message, conversation_id: str) -> None:
        """Store a message in the backend."""
        pass
    
    @abstractmethod
    async def retrieve_messages(
        self, 
        conversation_id: str, 
        limit: Optional[int] = None
    ) -> List[Message]:
        """Retrieve messages from a conversation."""
        pass
    
    @abstractmethod
    async def search_messages(
        self, 
        query: str, 
        user_id: Optional[str] = None, 
        limit: int = 10
    ) -> List[Message]:
        """Search for messages using text or semantic search."""
        pass
    
    # Memory Operations (Abstract)
    
    @abstractmethod
    async def store_memory(self, memory_entry: MemoryEntry) -> None:
        """Store a memory entry."""
        pass
    
    @abstractmethod
    async def retrieve_memories(self, query: MemoryQuery) -> List[MemoryEntry]:
        """Retrieve memories based on query."""
        pass
    
    @abstractmethod
    async def delete_memory(self, memory_id: str) -> None:
        """Delete a memory entry."""
        pass
    
    # Session Management (Abstract)
    
    @abstractmethod
    async def create_session(
        self, 
        user_id: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> SessionContext:
        """Create a new session."""
        pass
    
    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[SessionContext]:
        """Get session by ID."""
        pass
    
    @abstractmethod
    async def end_session(self, session_id: str) -> None:
        """End a session."""
        pass
    
    # Context Operations (Implemented with common logic)
    
    async def get_context(
        self, 
        user_id: str, 
        session_id: Optional[str] = None
    ) -> ConversationContext:
        """Get conversation context for user/session.
        
        This method provides a default implementation that can be 
        overridden by backends for optimization.
        """
        try:
            # Get session if session_id provided
            session = None
            if session_id:
                session = await self.get_session(session_id)
                if not session:
                    raise SessionError(f"Session not found: {session_id}")
            
            # Get user context (implementation-specific)
            user_context = await self._get_user_context(user_id)
            
            # Get recent messages from the conversation
            conversation_id = session.conversation_id if session else f"user_{user_id}"
            messages = await self.retrieve_messages(conversation_id, limit=100)
            
            # Build conversation context
            return ConversationContext(
                conversation_id=conversation_id,
                user=user_context,
                session=session,
                messages=messages,
                max_messages=100,
                metadata={}
            )
            
        except Exception as e:
            raise ContextBuildingError(f"Failed to build context: {e}") from e
    
    async def clear_history(
        self, 
        conversation_id: str, 
        keep_system_messages: bool = True
    ) -> None:
        """Clear conversation history.
        
        Default implementation - can be optimized by specific backends.
        """
        try:
            # Get all messages
            messages = await self.retrieve_messages(conversation_id)
            
            # Determine which messages to delete
            if keep_system_messages:
                # Delete only non-system messages (implementation-specific)
                await self._delete_non_system_messages(conversation_id, messages)
            else:
                # Delete all messages (implementation-specific)
                await self._delete_all_messages(conversation_id, messages)
                
        except Exception as e:
            raise StorageError(f"Failed to clear history: {e}") from e
    
    async def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get usage statistics for user.
        
        Default implementation provides basic stats.
        """
        try:
            # Get basic statistics (can be overridden for optimization)
            stats = await self._get_basic_statistics(user_id)
            
            return {
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **stats
            }
            
        except Exception as e:
            raise RetrievalError(f"Failed to get statistics: {e}") from e
    
    # Helper methods (can be overridden by backends)
    
    @abstractmethod
    async def _get_user_context(self, user_id: str) -> UserContext:
        """Get user context - must be implemented by backends."""
        pass
    
    @abstractmethod 
    async def _delete_non_system_messages(
        self, 
        conversation_id: str, 
        messages: List[Message]
    ) -> None:
        """Delete non-system messages - must be implemented by backends."""
        pass
    
    @abstractmethod
    async def _delete_all_messages(
        self, 
        conversation_id: str, 
        messages: List[Message]
    ) -> None:
        """Delete all messages - must be implemented by backends."""
        pass
    
    @abstractmethod
    async def _get_basic_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get basic statistics - must be implemented by backends."""
        pass
    
    # Utility methods (common to all backends)
    
    def serialize_message(self, message: Message) -> Dict[str, Any]:
        """Serialize message to dictionary for storage."""
        return {
            "id": message.id,
            "role": message.role.value,
            "content": message.content,
            "message_type": message.message_type.value if message.message_type else None,
            "timestamp": message.timestamp.isoformat(),
            "metadata": json.dumps(message.metadata) if message.metadata else "{}",
            "parent_id": message.parent_id,
            "conversation_id": message.conversation_id,
        }
    
    def deserialize_message(self, data: Dict[str, Any]) -> Message:
        """Deserialize message from dictionary."""
        try:
            return Message(
                id=data["id"],
                role=MessageRole(data["role"]),
                content=data["content"],
                message_type=data.get("message_type"),
                timestamp=datetime.fromisoformat(data["timestamp"]),
                metadata=json.loads(data["metadata"]) if data.get("metadata") and data["metadata"] != "{}" else {},
                parent_id=data.get("parent_id"),
                conversation_id=data.get("conversation_id"),
            )
        except (KeyError, ValueError, TypeError) as e:
            raise RetrievalError(f"Failed to deserialize message: {e}") from e
    
    def serialize_memory_entry(self, entry: MemoryEntry) -> Dict[str, Any]:
        """Serialize memory entry to dictionary for storage."""
        return {
            "id": entry.id,
            "content": entry.content,
            "memory_type": entry.memory_type.value if entry.memory_type else None,
            "user_id": entry.user_id,
            "conversation_id": entry.conversation_id,
            "metadata": json.dumps(entry.metadata) if entry.metadata else None,
            "created_at": entry.created_at.isoformat(),
            "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
            "last_accessed": entry.last_accessed.isoformat() if entry.last_accessed else None,
            "expires_at": entry.expires_at.isoformat() if entry.expires_at else None,
        }
    
    def deserialize_memory_entry(self, data: Dict[str, Any]) -> MemoryEntry:
        """Deserialize memory entry from dictionary."""
        try:
            return MemoryEntry(
                id=data["id"],
                content=data["content"],
                memory_type=data.get("memory_type"),
                user_id=data["user_id"],
                conversation_id=data.get("conversation_id"),
                metadata=json.loads(data["metadata"]) if data.get("metadata") else None,
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
                last_accessed=datetime.fromisoformat(data["last_accessed"]) if data.get("last_accessed") else None,
                expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            )
        except (KeyError, ValueError, TypeError) as e:
            raise RetrievalError(f"Failed to deserialize memory entry: {e}") from e
    
    def validate_query(self, query: MemoryQuery) -> None:
        """Validate memory query parameters."""
        if not query.query_text and not query.user_id:
            raise InvalidQueryError("Query must have either query_text or user_id")
        
        if query.limit and query.limit <= 0:
            raise InvalidQueryError("Query limit must be positive")
        
        if query.similarity_threshold and not (0.0 <= query.similarity_threshold <= 1.0):
            raise InvalidQueryError("Similarity threshold must be between 0.0 and 1.0")
    
    def get_current_timestamp(self) -> datetime:
        """Get current timestamp with timezone info."""
        return datetime.now(timezone.utc)
    
    async def __aenter__(self):
        """Async context manager entry."""
        if not self._initialized:
            await self.initialize()
            self._initialized = True
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if not self._closed:
            await self.close()
            self._closed = True