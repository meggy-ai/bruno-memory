"""
Abstract base backend implementation for memory storage.

Provides common functionality and interface compliance for all backend types.
"""

import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from bruno_core.interfaces.memory_interface import MemoryInterface
from bruno_core.models import (
    Message, 
    MemoryEntry, 
    MemoryQuery, 
    SessionContext, 
    ConversationContext, 
    UserContext
)

from ..base.memory_config import MemoryConfig
from ..exceptions import ValidationError, SerializationError


class BaseMemoryBackend(MemoryInterface, ABC):
    """Abstract base class for all memory backends."""
    
    def __init__(self, config: MemoryConfig):
        """Initialize the backend with configuration.
        
        Args:
            config: Backend configuration
        """
        self.config = config
        self._connected = False
    
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the storage backend."""
        pass
    
    @abstractmethod 
    async def disconnect(self) -> None:
        """Disconnect from the storage backend."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the backend is healthy and accessible."""
        pass
    
    # Utility methods for serialization/deserialization
    
    def serialize_message(self, message: Message) -> Dict[str, Any]:
        """Serialize a Message object to dictionary.
        
        Args:
            message: Message to serialize
            
        Returns:
            Serialized message dictionary
            
        Raises:
            SerializationError: If serialization fails
        """
        try:
            return {
                "id": str(message.id),
                "conversation_id": message.conversation_id,
                "role": message.role.value if hasattr(message.role, 'value') else str(message.role),
                "content": message.content,
                "timestamp": message.timestamp.isoformat() if message.timestamp else None,
                "message_type": message.message_type.value if hasattr(message.message_type, 'value') else str(message.message_type),
                "metadata": json.dumps(message.metadata) if message.metadata else None,
                "user_id": message.user_id,
                "parent_id": str(message.parent_id) if message.parent_id else None,
                "tokens": message.tokens,
                "model": message.model,
                "finish_reason": message.finish_reason
            }
        except Exception as e:
            raise SerializationError(f"Failed to serialize message: {e}")
    
    def deserialize_message(self, data: Dict[str, Any]) -> Message:
        """Deserialize dictionary to Message object.
        
        Args:
            data: Serialized message data
            
        Returns:
            Message object
            
        Raises:
            SerializationError: If deserialization fails
        """
        try:
            # Handle metadata JSON deserialization
            metadata = None
            if data.get("metadata"):
                metadata = json.loads(data["metadata"])
            
            # Parse timestamp
            timestamp = None
            if data.get("timestamp"):
                timestamp = datetime.fromisoformat(data["timestamp"])
            
            return Message(
                id=data["id"],
                conversation_id=data["conversation_id"], 
                role=data["role"],
                content=data["content"],
                timestamp=timestamp,
                message_type=data.get("message_type"),
                metadata=metadata,
                user_id=data.get("user_id"),
                parent_id=data.get("parent_id"),
                tokens=data.get("tokens"),
                model=data.get("model"),
                finish_reason=data.get("finish_reason")
            )
        except Exception as e:
            raise SerializationError(f"Failed to deserialize message: {e}")
    
    def serialize_memory_entry(self, memory: MemoryEntry) -> Dict[str, Any]:
        """Serialize a MemoryEntry object to dictionary.
        
        Args:
            memory: MemoryEntry to serialize
            
        Returns:
            Serialized memory dictionary
            
        Raises:
            SerializationError: If serialization fails
        """
        try:
            return {
                "id": str(memory.id),
                "content": memory.content,
                "memory_type": memory.memory_type.value if hasattr(memory.memory_type, 'value') else str(memory.memory_type),
                "importance": memory.importance,
                "timestamp": memory.timestamp.isoformat(),
                "user_id": memory.user_id,
                "conversation_id": memory.conversation_id,
                "tags": json.dumps(memory.tags) if memory.tags else None,
                "metadata": json.dumps(memory.metadata.dict()) if memory.metadata else None,
                "embedding": json.dumps(memory.embedding) if memory.embedding else None,
                "expires_at": memory.expires_at.isoformat() if memory.expires_at else None
            }
        except Exception as e:
            raise SerializationError(f"Failed to serialize memory entry: {e}")
    
    def deserialize_memory_entry(self, data: Dict[str, Any]) -> MemoryEntry:
        """Deserialize dictionary to MemoryEntry object.
        
        Args:
            data: Serialized memory data
            
        Returns:
            MemoryEntry object
            
        Raises:
            SerializationError: If deserialization fails  
        """
        try:
            # Handle JSON fields
            tags = json.loads(data["tags"]) if data.get("tags") else []
            metadata = json.loads(data["metadata"]) if data.get("metadata") else None
            embedding = json.loads(data["embedding"]) if data.get("embedding") else None
            
            # Parse timestamps
            timestamp = datetime.fromisoformat(data["timestamp"])
            expires_at = None
            if data.get("expires_at"):
                expires_at = datetime.fromisoformat(data["expires_at"])
            
            return MemoryEntry(
                id=data["id"],
                content=data["content"],
                memory_type=data["memory_type"],
                importance=data["importance"],
                timestamp=timestamp,
                user_id=data["user_id"],
                conversation_id=data.get("conversation_id"),
                tags=tags,
                metadata=metadata,
                embedding=embedding,
                expires_at=expires_at
            )
        except Exception as e:
            raise SerializationError(f"Failed to deserialize memory entry: {e}")
    
    def serialize_session_context(self, session: SessionContext) -> Dict[str, Any]:
        """Serialize a SessionContext object to dictionary.
        
        Args:
            session: SessionContext to serialize
            
        Returns:
            Serialized session dictionary
            
        Raises:
            SerializationError: If serialization fails
        """
        try:
            return {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "conversation_id": session.conversation_id,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat() if session.updated_at else None,
                "metadata": json.dumps(session.metadata) if session.metadata else None,
                "is_active": session.is_active
            }
        except Exception as e:
            raise SerializationError(f"Failed to serialize session context: {e}")
    
    def deserialize_session_context(self, data: Dict[str, Any]) -> SessionContext:
        """Deserialize dictionary to SessionContext object.
        
        Args:
            data: Serialized session data
            
        Returns:
            SessionContext object
            
        Raises:
            SerializationError: If deserialization fails
        """
        try:
            metadata = json.loads(data["metadata"]) if data.get("metadata") else None
            created_at = datetime.fromisoformat(data["created_at"])
            updated_at = None
            if data.get("updated_at"):
                updated_at = datetime.fromisoformat(data["updated_at"])
            
            return SessionContext(
                session_id=data["session_id"],
                user_id=data["user_id"],
                conversation_id=data["conversation_id"],
                created_at=created_at,
                updated_at=updated_at,
                metadata=metadata,
                is_active=data.get("is_active", True)
            )
        except Exception as e:
            raise SerializationError(f"Failed to deserialize session context: {e}")
    
    def generate_id(self) -> str:
        """Generate a unique ID for messages/entries."""
        return str(uuid4())
    
    def validate_message(self, message: Message) -> None:
        """Validate a Message object.
        
        Args:
            message: Message to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if not message.id:
            raise ValidationError("Message ID is required")
        if not message.conversation_id:
            raise ValidationError("Conversation ID is required")
        if not message.content:
            raise ValidationError("Message content is required")
        if not message.role:
            raise ValidationError("Message role is required")
    
    def validate_memory_entry(self, memory: MemoryEntry) -> None:
        """Validate a MemoryEntry object.
        
        Args:
            memory: MemoryEntry to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if not memory.id:
            raise ValidationError("Memory entry ID is required") 
        if not memory.content:
            raise ValidationError("Memory entry content is required")
        if not memory.user_id:
            raise ValidationError("Memory entry user_id is required")
        if memory.importance is not None and not (0.0 <= memory.importance <= 1.0):
            raise ValidationError("Memory entry importance must be between 0.0 and 1.0")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit.""" 
        await self.disconnect()