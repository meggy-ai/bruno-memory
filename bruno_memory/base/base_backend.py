"""
Base backend implementation for bruno-memory.

This module provides the abstract base class that all memory backend
implementations should extend. It includes common functionality and
enforces the MemoryInterface contract from bruno-core.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from bruno_core.interfaces import MemoryInterface
from bruno_core.models import Message, MessageRole
from bruno_core.models.context import ConversationContext, SessionContext
from bruno_core.models.memory import MemoryEntry, MemoryQuery

from bruno_memory.exceptions import (
    MemoryError,
    SerializationError,
    StorageError,
    ValidationError,
)


class BaseMemoryBackend(MemoryInterface, ABC):
    """
    Abstract base class for all memory backends.

    Provides common functionality for message serialization, validation,
    and utility methods that all backends can use. Concrete backends
    must implement the abstract methods defined here.

    Args:
        backend_name: Name of the backend (e.g., "sqlite", "postgresql")
        config: Backend-specific configuration

    Example:
        >>> class MyBackend(BaseMemoryBackend):
        ...     def __init__(self, **config):
        ...         super().__init__("mybackend", config)
        ...
        ...     async def store_message(self, message, conversation_id):
        ...         # Implementation
        ...         pass
    """

    def __init__(self, backend_name: str, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize base memory backend.

        Args:
            backend_name: Identifier for this backend
            config: Configuration dictionary
        """
        self.backend_name = backend_name
        self.config = config or {}
        self._initialized = False

    def _serialize_message(self, message: Message) -> Dict[str, Any]:
        """
        Serialize a Message object to a dictionary.

        Args:
            message: Message to serialize

        Returns:
            Dictionary representation of message

        Raises:
            SerializationError: If serialization fails
        """
        try:
            return {
                "role": message.role.value,
                "content": message.content,
                "name": message.name,
                "metadata": message.metadata,
                "timestamp": message.timestamp.isoformat() if message.timestamp else None,
            }
        except Exception as e:
            raise SerializationError(
                f"Failed to serialize message: {e}", details={"message": str(message)}
            )

    def _deserialize_message(self, data: Dict[str, Any]) -> Message:
        """
        Deserialize a dictionary to a Message object.

        Args:
            data: Dictionary containing message data

        Returns:
            Message object

        Raises:
            SerializationError: If deserialization fails
        """
        try:
            # Parse timestamp if present
            timestamp = None
            if data.get("timestamp"):
                if isinstance(data["timestamp"], str):
                    timestamp = datetime.fromisoformat(data["timestamp"])
                elif isinstance(data["timestamp"], datetime):
                    timestamp = data["timestamp"]

            return Message(
                role=MessageRole(data["role"]),
                content=data["content"],
                name=data.get("name"),
                metadata=data.get("metadata", {}),
                timestamp=timestamp,
            )
        except Exception as e:
            raise SerializationError(
                f"Failed to deserialize message: {e}", details={"data": data}
            )

    def _validate_conversation_id(self, conversation_id: str) -> None:
        """
        Validate conversation ID format.

        Args:
            conversation_id: ID to validate

        Raises:
            ValidationError: If validation fails
        """
        if not conversation_id or not isinstance(conversation_id, str):
            raise ValidationError(
                "Conversation ID must be a non-empty string",
                details={"conversation_id": conversation_id},
            )

        if len(conversation_id) > 255:
            raise ValidationError(
                "Conversation ID too long (max 255 characters)",
                details={"length": len(conversation_id)},
            )

    def _validate_user_id(self, user_id: str) -> None:
        """
        Validate user ID format.

        Args:
            user_id: ID to validate

        Raises:
            ValidationError: If validation fails
        """
        if not user_id or not isinstance(user_id, str):
            raise ValidationError(
                "User ID must be a non-empty string", details={"user_id": user_id}
            )

        if len(user_id) > 255:
            raise ValidationError(
                "User ID too long (max 255 characters)", details={"length": len(user_id)}
            )

    def _validate_message(self, message: Message) -> None:
        """
        Validate message object.

        Args:
            message: Message to validate

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(message, Message):
            raise ValidationError(
                "Invalid message type", details={"type": type(message).__name__}
            )

        if not message.content:
            raise ValidationError("Message content cannot be empty")

        if len(message.content) > 1_000_000:  # 1MB limit
            raise ValidationError(
                "Message content too large (max 1MB)",
                details={"size": len(message.content)},
            )

    def get_backend_info(self) -> Dict[str, Any]:
        """
        Get information about this backend.

        Returns:
            Dictionary with backend details
        """
        return {
            "backend": self.backend_name,
            "initialized": self._initialized,
            "config": {k: v for k, v in self.config.items() if "password" not in k.lower()},
        }

    async def initialize(self) -> None:
        """
        Initialize the backend.

        Override this method to perform any setup required
        (e.g., database connection, creating tables).
        """
        self._initialized = True

    async def close(self) -> None:
        """
        Close the backend and cleanup resources.

        Override this method to perform cleanup
        (e.g., closing database connections).
        """
        self._initialized = False

    # Abstract methods that concrete backends must implement

    @abstractmethod
    async def store_message(self, message: Message, conversation_id: str) -> None:
        """
        Store a message in the backend.

        Args:
            message: Message to store
            conversation_id: Conversation this message belongs to

        Raises:
            StorageError: If storage fails
        """
        pass

    @abstractmethod
    async def retrieve_messages(
        self, conversation_id: str, limit: Optional[int] = None
    ) -> List[Message]:
        """
        Retrieve messages from a conversation.

        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages to retrieve

        Returns:
            List of messages (most recent first)

        Raises:
            RetrievalError: If retrieval fails
        """
        pass

    @abstractmethod
    async def search_messages(
        self, query: str, user_id: Optional[str] = None, limit: int = 10
    ) -> List[Message]:
        """
        Search messages by text query.

        Args:
            query: Search query
            user_id: Optional user ID to filter by
            limit: Maximum results

        Returns:
            List of matching messages

        Raises:
            RetrievalError: If search fails
        """
        pass

    @abstractmethod
    async def store_memory(self, memory_entry: MemoryEntry) -> None:
        """
        Store a memory entry.

        Args:
            memory_entry: Memory entry to store

        Raises:
            StorageError: If storage fails
        """
        pass

    @abstractmethod
    async def retrieve_memories(self, query: MemoryQuery) -> List[MemoryEntry]:
        """
        Retrieve memories matching query criteria.

        Args:
            query: Memory query with filters

        Returns:
            List of matching memory entries

        Raises:
            RetrievalError: If retrieval fails
        """
        pass

    @abstractmethod
    async def delete_memory(self, memory_id: str) -> None:
        """
        Delete a memory entry.

        Args:
            memory_id: Memory entry ID

        Raises:
            MemoryError: If deletion fails
        """
        pass

    @abstractmethod
    async def create_session(
        self, user_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> SessionContext:
        """
        Create a new conversation session.

        Args:
            user_id: User ID
            metadata: Optional session metadata

        Returns:
            Session context

        Raises:
            SessionError: If creation fails
        """
        pass

    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[SessionContext]:
        """
        Retrieve a session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session context or None if not found
        """
        pass

    @abstractmethod
    async def end_session(self, session_id: str) -> None:
        """
        End a conversation session.

        Args:
            session_id: Session ID

        Raises:
            SessionError: If session not found
        """
        pass

    @abstractmethod
    async def get_context(
        self, user_id: str, session_id: Optional[str] = None
    ) -> ConversationContext:
        """
        Get conversation context for a user.

        Args:
            user_id: User ID
            session_id: Optional session ID

        Returns:
            Conversation context

        Raises:
            ContextError: If context cannot be retrieved
        """
        pass

    @abstractmethod
    async def clear_history(
        self, conversation_id: str, keep_system_messages: bool = True
    ) -> None:
        """
        Clear message history for a conversation.

        Args:
            conversation_id: Conversation ID
            keep_system_messages: Whether to keep system messages

        Raises:
            MemoryError: If clearing fails
        """
        pass

    @abstractmethod
    async def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get memory statistics for a user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with statistics

        Raises:
            AnalyticsError: If statistics retrieval fails
        """
        pass

    # Context manager support

    async def __aenter__(self) -> "BaseMemoryBackend":
        """Context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        await self.close()
