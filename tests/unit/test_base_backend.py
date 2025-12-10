"""
Unit tests for base backend functionality.

Tests the BaseMemoryBackend abstract class and common utilities.
"""

import pytest
from datetime import datetime
from typing import Any, Dict, List, Optional

from bruno_core.models import Message, MessageRole
from bruno_core.models.context import ConversationContext, SessionContext
from bruno_core.models.memory import MemoryEntry, MemoryQuery

from bruno_memory.base import BaseMemoryBackend
from bruno_memory.exceptions import SerializationError, ValidationError


class MockBackend(BaseMemoryBackend):
    """Mock backend implementation for testing."""

    def __init__(self, **config):
        super().__init__("mock", config)
        self.messages: Dict[str, List[Message]] = {}
        self.memories: List[MemoryEntry] = []
        self.sessions: Dict[str, SessionContext] = {}

    async def store_message(self, message: Message, conversation_id: str) -> None:
        """Store message in memory."""
        if conversation_id not in self.messages:
            self.messages[conversation_id] = []
        self.messages[conversation_id].append(message)

    async def retrieve_messages(
        self, conversation_id: str, limit: Optional[int] = None
    ) -> List[Message]:
        """Retrieve messages."""
        messages = self.messages.get(conversation_id, [])
        if limit:
            return messages[-limit:]
        return messages

    async def search_messages(
        self, query: str, user_id: Optional[str] = None, limit: int = 10
    ) -> List[Message]:
        """Search messages."""
        results = []
        for msgs in self.messages.values():
            for msg in msgs:
                if query.lower() in msg.content.lower():
                    results.append(msg)
        return results[:limit]

    async def store_memory(self, memory_entry: MemoryEntry) -> None:
        """Store memory."""
        self.memories.append(memory_entry)

    async def retrieve_memories(self, query: MemoryQuery) -> List[MemoryEntry]:
        """Retrieve memories."""
        return [m for m in self.memories if m.user_id == query.user_id]

    async def delete_memory(self, memory_id: str) -> None:
        """Delete memory."""
        self.memories = [m for m in self.memories if str(m.id) != memory_id]

    async def create_session(
        self, user_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> SessionContext:
        """Create session."""
        session = SessionContext(user_id=user_id, metadata=metadata or {})
        self.sessions[str(session.session_id)] = session
        return session

    async def get_session(self, session_id: str) -> Optional[SessionContext]:
        """Get session."""
        return self.sessions.get(session_id)

    async def end_session(self, session_id: str) -> None:
        """End session."""
        if session_id in self.sessions:
            del self.sessions[session_id]

    async def get_context(
        self, user_id: str, session_id: Optional[str] = None
    ) -> ConversationContext:
        """Get context."""
        messages = []
        for msgs in self.messages.values():
            messages.extend(msgs)
        return ConversationContext(messages=messages[-10:])

    async def clear_history(
        self, conversation_id: str, keep_system_messages: bool = True
    ) -> None:
        """Clear history."""
        if conversation_id in self.messages:
            if keep_system_messages:
                self.messages[conversation_id] = [
                    m for m in self.messages[conversation_id] if m.role == MessageRole.SYSTEM
                ]
            else:
                del self.messages[conversation_id]

    async def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get statistics."""
        return {"total_messages": sum(len(msgs) for msgs in self.messages.values())}


class TestBaseMemoryBackend:
    """Test suite for BaseMemoryBackend."""

    @pytest.fixture
    def backend(self) -> MockBackend:
        """Create mock backend."""
        return MockBackend(test_config="value")

    @pytest.fixture
    def sample_message(self) -> Message:
        """Create sample message."""
        return Message(role=MessageRole.USER, content="Test message")

    def test_backend_initialization(self, backend: MockBackend):
        """Test backend initialization."""
        assert backend.backend_name == "mock"
        assert backend.config == {"test_config": "value"}
        assert not backend._initialized

    @pytest.mark.asyncio
    async def test_initialize_and_close(self, backend: MockBackend):
        """Test initialize and close methods."""
        await backend.initialize()
        assert backend._initialized

        await backend.close()
        assert not backend._initialized

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test context manager support."""
        async with MockBackend() as backend:
            assert backend._initialized

    def test_get_backend_info(self, backend: MockBackend):
        """Test get_backend_info method."""
        info = backend.get_backend_info()
        assert info["backend"] == "mock"
        assert "config" in info
        assert info["config"]["test_config"] == "value"

    def test_serialize_message(self, backend: MockBackend, sample_message: Message):
        """Test message serialization."""
        serialized = backend._serialize_message(sample_message)

        assert serialized["role"] == "user"
        assert serialized["content"] == "Test message"
        assert "metadata" in serialized

    def test_deserialize_message(self, backend: MockBackend):
        """Test message deserialization."""
        data = {
            "role": "user",
            "content": "Test message",
            "metadata": {"key": "value"},
        }

        message = backend._deserialize_message(data)

        assert isinstance(message, Message)
        assert message.role == MessageRole.USER
        assert message.content == "Test message"
        assert message.metadata == {"key": "value"}

    def test_deserialize_message_with_timestamp(self, backend: MockBackend):
        """Test message deserialization with timestamp."""
        timestamp = datetime.now()
        data = {
            "role": "assistant",
            "content": "Response",
            "timestamp": timestamp.isoformat(),
        }

        message = backend._deserialize_message(data)

        assert message.timestamp is not None
        assert message.timestamp.date() == timestamp.date()

    def test_serialize_deserialize_roundtrip(self, backend: MockBackend, sample_message: Message):
        """Test serialization/deserialization roundtrip."""
        serialized = backend._serialize_message(sample_message)
        deserialized = backend._deserialize_message(serialized)

        assert deserialized.role == sample_message.role
        assert deserialized.content == sample_message.content

    def test_validate_conversation_id_valid(self, backend: MockBackend):
        """Test valid conversation ID."""
        backend._validate_conversation_id("conv_123")  # Should not raise

    def test_validate_conversation_id_empty(self, backend: MockBackend):
        """Test empty conversation ID."""
        with pytest.raises(ValidationError) as exc_info:
            backend._validate_conversation_id("")
        assert "non-empty string" in str(exc_info.value)

    def test_validate_conversation_id_too_long(self, backend: MockBackend):
        """Test conversation ID too long."""
        long_id = "x" * 300
        with pytest.raises(ValidationError) as exc_info:
            backend._validate_conversation_id(long_id)
        assert "too long" in str(exc_info.value)

    def test_validate_conversation_id_invalid_type(self, backend: MockBackend):
        """Test invalid conversation ID type."""
        with pytest.raises(ValidationError):
            backend._validate_conversation_id(None)

    def test_validate_user_id_valid(self, backend: MockBackend):
        """Test valid user ID."""
        backend._validate_user_id("user_456")  # Should not raise

    def test_validate_user_id_invalid(self, backend: MockBackend):
        """Test invalid user ID."""
        with pytest.raises(ValidationError):
            backend._validate_user_id("")

    def test_validate_message_valid(self, backend: MockBackend, sample_message: Message):
        """Test valid message."""
        backend._validate_message(sample_message)  # Should not raise

    def test_validate_message_empty_content(self, backend: MockBackend):
        """Test message with empty content."""
        message = Message(role=MessageRole.USER, content="")
        with pytest.raises(ValidationError) as exc_info:
            backend._validate_message(message)
        assert "content cannot be empty" in str(exc_info.value)

    def test_validate_message_too_large(self, backend: MockBackend):
        """Test message with content too large."""
        large_content = "x" * 1_000_001
        message = Message(role=MessageRole.USER, content=large_content)
        with pytest.raises(ValidationError) as exc_info:
            backend._validate_message(message)
        assert "too large" in str(exc_info.value)

    def test_validate_message_invalid_type(self, backend: MockBackend):
        """Test invalid message type."""
        with pytest.raises(ValidationError):
            backend._validate_message("not a message")

    @pytest.mark.asyncio
    async def test_store_and_retrieve_message(self, backend: MockBackend, sample_message: Message):
        """Test storing and retrieving messages."""
        await backend.store_message(sample_message, "conv_123")

        messages = await backend.retrieve_messages("conv_123")
        assert len(messages) == 1
        assert messages[0].content == "Test message"

    @pytest.mark.asyncio
    async def test_retrieve_messages_with_limit(self, backend: MockBackend):
        """Test retrieving messages with limit."""
        # Store multiple messages
        for i in range(5):
            msg = Message(role=MessageRole.USER, content=f"Message {i}")
            await backend.store_message(msg, "conv_123")

        # Retrieve with limit
        messages = await backend.retrieve_messages("conv_123", limit=3)
        assert len(messages) == 3

    @pytest.mark.asyncio
    async def test_search_messages(self, backend: MockBackend):
        """Test searching messages."""
        msg1 = Message(role=MessageRole.USER, content="Set a timer for 5 minutes")
        msg2 = Message(role=MessageRole.USER, content="What's the weather?")

        await backend.store_message(msg1, "conv_1")
        await backend.store_message(msg2, "conv_2")

        results = await backend.search_messages("timer")
        assert len(results) == 1
        assert "timer" in results[0].content.lower()

    @pytest.mark.asyncio
    async def test_clear_history_keep_system(self, backend: MockBackend):
        """Test clearing history while keeping system messages."""
        system_msg = Message(role=MessageRole.SYSTEM, content="System prompt")
        user_msg = Message(role=MessageRole.USER, content="User message")

        await backend.store_message(system_msg, "conv_123")
        await backend.store_message(user_msg, "conv_123")

        await backend.clear_history("conv_123", keep_system_messages=True)

        messages = await backend.retrieve_messages("conv_123")
        assert len(messages) == 1
        assert messages[0].role == MessageRole.SYSTEM

    @pytest.mark.asyncio
    async def test_clear_history_delete_all(self, backend: MockBackend):
        """Test clearing all history."""
        system_msg = Message(role=MessageRole.SYSTEM, content="System prompt")
        user_msg = Message(role=MessageRole.USER, content="User message")

        await backend.store_message(system_msg, "conv_123")
        await backend.store_message(user_msg, "conv_123")

        await backend.clear_history("conv_123", keep_system_messages=False)

        messages = await backend.retrieve_messages("conv_123")
        assert len(messages) == 0

    @pytest.mark.asyncio
    async def test_session_lifecycle(self, backend: MockBackend):
        """Test session creation, retrieval, and ending."""
        # Create session
        session = await backend.create_session("user_123", {"key": "value"})
        assert session.user_id == "user_123"
        assert session.metadata["key"] == "value"

        # Retrieve session
        retrieved = await backend.get_session(str(session.session_id))
        assert retrieved is not None
        assert retrieved.user_id == "user_123"

        # End session
        await backend.end_session(str(session.session_id))
        ended = await backend.get_session(str(session.session_id))
        assert ended is None

    @pytest.mark.asyncio
    async def test_get_statistics(self, backend: MockBackend):
        """Test getting statistics."""
        msg1 = Message(role=MessageRole.USER, content="Message 1")
        msg2 = Message(role=MessageRole.USER, content="Message 2")

        await backend.store_message(msg1, "conv_1")
        await backend.store_message(msg2, "conv_1")

        stats = await backend.get_statistics("user_123")
        assert "total_messages" in stats
        assert stats["total_messages"] == 2
