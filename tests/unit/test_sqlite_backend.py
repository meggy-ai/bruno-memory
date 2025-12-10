"""Tests for SQLite backend."""

import pytest
from datetime import datetime, timedelta
from bruno_core.models import Message, MemoryEntry, MemoryQuery, MemoryType
from bruno_memory.backends.sqlite import SQLiteMemoryBackend
from bruno_memory.exceptions import ConnectionError, ValidationError, OperationError


class TestSQLiteBackend:
    """Test cases for SQLite backend."""
    
    async def test_connection(self, sqlite_backend):
        """Test database connection."""
        assert sqlite_backend._connected is True
        assert await sqlite_backend.health_check() is True
    
    async def test_store_and_retrieve_message(self, sqlite_backend, sample_message):
        """Test storing and retrieving messages."""
        # Store message
        await sqlite_backend.store_message(sample_message, sample_message.conversation_id)
        
        # Retrieve messages
        messages = await sqlite_backend.retrieve_messages(sample_message.conversation_id)
        
        assert len(messages) == 1
        retrieved_message = messages[0]
        assert retrieved_message.id == sample_message.id
        assert retrieved_message.content == sample_message.content
        assert retrieved_message.role == sample_message.role
        assert retrieved_message.conversation_id == sample_message.conversation_id
    
    async def test_search_messages(self, sqlite_backend, sample_message):
        """Test searching messages."""
        # Store message
        await sqlite_backend.store_message(sample_message, sample_message.conversation_id)
        
        # Search for the message
        results = await sqlite_backend.search_messages("Hello")
        
        assert len(results) == 1
        assert results[0].id == sample_message.id
    
    async def test_store_and_retrieve_memory(self, sqlite_backend, sample_memory_entry):
        """Test storing and retrieving memory entries."""
        # Store memory
        await sqlite_backend.store_memory(sample_memory_entry)
        
        # Create query to retrieve memory
        query = MemoryQuery(
            user_id=sample_memory_entry.user_id,
            limit=10
        )
        
        # Retrieve memories
        memories = await sqlite_backend.retrieve_memories(query)
        
        assert len(memories) == 1
        retrieved_memory = memories[0]
        assert retrieved_memory.id == sample_memory_entry.id
        assert retrieved_memory.content == sample_memory_entry.content
        assert retrieved_memory.user_id == sample_memory_entry.user_id
    
    async def test_delete_memory(self, sqlite_backend, sample_memory_entry):
        """Test deleting memory entries."""
        # Store memory
        await sqlite_backend.store_memory(sample_memory_entry)
        
        # Verify it exists
        query = MemoryQuery(user_id=sample_memory_entry.user_id)
        memories = await sqlite_backend.retrieve_memories(query)
        assert len(memories) == 1
        
        # Delete memory
        await sqlite_backend.delete_memory(sample_memory_entry.id)
        
        # Verify it's deleted
        memories = await sqlite_backend.retrieve_memories(query)
        assert len(memories) == 0
    
    async def test_create_and_get_session(self, sqlite_backend):
        """Test session management."""
        user_id = "test-user-session"
        metadata = {"test": "data"}
        
        # Create session
        session = await sqlite_backend.create_session(user_id, metadata)
        
        assert session.user_id == user_id
        assert session.metadata == metadata
        assert session.is_active is True
        assert session.session_id is not None
        assert session.conversation_id is not None
        
        # Get session
        retrieved_session = await sqlite_backend.get_session(session.session_id)
        
        assert retrieved_session is not None
        assert retrieved_session.session_id == session.session_id
        assert retrieved_session.user_id == user_id
        assert retrieved_session.metadata == metadata
    
    async def test_end_session(self, sqlite_backend):
        """Test ending a session."""
        user_id = "test-user-end-session"
        
        # Create session
        session = await sqlite_backend.create_session(user_id)
        assert session.is_active is True
        
        # End session
        await sqlite_backend.end_session(session.session_id)
        
        # Verify session is ended
        retrieved_session = await sqlite_backend.get_session(session.session_id)
        assert retrieved_session.is_active is False
    
    async def test_clear_history(self, sqlite_backend):
        """Test clearing conversation history."""
        conversation_id = "test-clear-conv"
        
        # Create multiple messages
        messages = []
        for i in range(3):
            message = Message(
                id=f"msg-{i}",
                conversation_id=conversation_id,
                role="user" if i % 2 == 0 else "assistant", 
                content=f"Message {i}",
                timestamp=datetime.now(),
                user_id="test-user"
            )
            messages.append(message)
            await sqlite_backend.store_message(message, conversation_id)
        
        # Verify messages exist
        retrieved_messages = await sqlite_backend.retrieve_messages(conversation_id)
        assert len(retrieved_messages) == 3
        
        # Clear history
        await sqlite_backend.clear_history(conversation_id)
        
        # Verify messages are cleared
        retrieved_messages = await sqlite_backend.retrieve_messages(conversation_id)
        assert len(retrieved_messages) == 0
    
    async def test_get_context(self, sqlite_backend):
        """Test getting conversation context."""
        conversation_id = "test-context-conv"
        user_id = "test-context-user"
        
        # Create a message
        message = Message(
            id="context-msg-1",
            conversation_id=conversation_id,
            role="user",
            content="Context test message",
            timestamp=datetime.now(),
            user_id=user_id
        )
        await sqlite_backend.store_message(message, conversation_id)
        
        # Get context
        context = await sqlite_backend.get_context(conversation_id, user_id)
        
        assert context.conversation_id == conversation_id
        assert len(context.messages) == 1
        assert context.messages[0].id == message.id
        assert context.user_context.user_id == user_id
    
    async def test_get_statistics(self, sqlite_backend, sample_message, sample_memory_entry):
        """Test getting user statistics."""
        user_id = "test-stats-user"
        
        # Update test data with consistent user_id
        sample_message.user_id = user_id
        sample_memory_entry.user_id = user_id
        
        # Store test data
        await sqlite_backend.store_message(sample_message, sample_message.conversation_id)
        await sqlite_backend.store_memory(sample_memory_entry)
        
        # Create a session
        await sqlite_backend.create_session(user_id)
        
        # Get statistics
        stats = await sqlite_backend.get_statistics(user_id)
        
        assert stats["message_count"] == 1
        assert stats["memory_count"] == 1
        assert stats["active_sessions"] == 1
        assert stats["conversation_count"] == 1
    
    async def test_validation_errors(self, sqlite_backend):
        """Test validation error handling."""
        # Test invalid message
        invalid_message = Message(
            id="",  # Empty ID should trigger validation error
            conversation_id="test-conv",
            role="user",
            content="Test content",
            timestamp=datetime.now()
        )
        
        with pytest.raises(ValidationError):
            await sqlite_backend.store_message(invalid_message, "test-conv")
    
    async def test_connection_error_handling(self, temp_db_path):
        """Test connection error handling."""
        from bruno_memory.base.memory_config import SQLiteConfig
        
        config = SQLiteConfig(database_path=temp_db_path)
        backend = SQLiteMemoryBackend(config)
        
        # Try operations without connecting
        with pytest.raises(ConnectionError):
            await backend.retrieve_messages("test-conv")
        
        with pytest.raises(ConnectionError):
            await backend.search_messages("test query")
    
    async def test_memory_query_filtering(self, sqlite_backend):
        """Test memory query filtering options."""
        user_id = "test-filter-user"
        conversation_id = "test-filter-conv"
        
        # Create multiple memory entries with different properties
        memories = [
            MemoryEntry(
                id="mem-1",
                content="Important memory about cats",
                memory_type=MemoryType.EPISODIC,
                importance=0.9,
                timestamp=datetime.now() - timedelta(hours=1),
                user_id=user_id,
                conversation_id=conversation_id,
                tags=["cats", "important"]
            ),
            MemoryEntry(
                id="mem-2", 
                content="Less important memory about dogs",
                memory_type=MemoryType.SEMANTIC,
                importance=0.3,
                timestamp=datetime.now(),
                user_id=user_id,
                conversation_id=conversation_id,
                tags=["dogs"]
            )
        ]
        
        for memory in memories:
            await sqlite_backend.store_memory(memory)
        
        # Test filtering by importance
        query = MemoryQuery(
            user_id=user_id,
            min_importance=0.5
        )
        results = await sqlite_backend.retrieve_memories(query)
        assert len(results) == 1
        assert results[0].id == "mem-1"
        
        # Test filtering by memory type
        query = MemoryQuery(
            user_id=user_id,
            memory_types=[MemoryType.SEMANTIC]
        )
        results = await sqlite_backend.retrieve_memories(query)
        assert len(results) == 1
        assert results[0].id == "mem-2"
        
        # Test text search
        query = MemoryQuery(
            user_id=user_id,
            query_text="cats"
        )
        results = await sqlite_backend.retrieve_memories(query)
        assert len(results) == 1
        assert results[0].id == "mem-1"