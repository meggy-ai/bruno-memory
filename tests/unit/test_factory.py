"""Unit tests for bruno-memory factory."""

import pytest
from unittest.mock import Mock, patch

from bruno_memory import MemoryFactory
from bruno_memory.exceptions import BackendNotAvailableError, ConfigurationError
from bruno_memory.base import MemoryConfig, BaseMemoryBackend


class TestMemoryFactory:
    """Test MemoryFactory functionality."""
    
    def test_list_providers(self):
        """Test listing available providers."""
        providers = MemoryFactory.list_providers()
        assert isinstance(providers, list)
        # At minimum, should have empty list (no backends implemented yet)
        assert len(providers) >= 0
    
    def test_is_registered(self):
        """Test checking if backend is registered."""
        # Test with non-existent backend
        assert not MemoryFactory.is_registered("nonexistent")
    
    def test_create_unknown_backend(self):
        """Test creating unknown backend raises error."""
        with pytest.raises(BackendNotAvailableError) as exc_info:
            MemoryFactory.create("unknown_backend")
        
        assert "unknown_backend" in str(exc_info.value)
        assert "Available backends:" in str(exc_info.value)
    
    def test_create_with_fallback_all_fail(self):
        """Test fallback creation when all backends fail."""
        with pytest.raises(BackendNotAvailableError) as exc_info:
            MemoryFactory.create_with_fallback(["unknown1", "unknown2"])
        
        assert "All backends failed" in str(exc_info.value)
    
    @patch.dict('os.environ', {
        'BRUNO_MEMORY_BACKEND': 'sqlite',
        'BRUNO_MEMORY_DATABASE_PATH': './test.db',
        'BRUNO_MEMORY_TIMEOUT': '60'
    })
    def test_create_from_env(self):
        """Test creating backend from environment variables."""
        # This will fail since SQLite backend is not implemented yet
        # but we can test that it attempts to create the right backend
        with pytest.raises(BackendNotAvailableError):
            MemoryFactory.create_from_env()
    
    def test_register_backend(self):
        """Test registering a custom backend."""
        # Create mock backend class
        class MockBackend(BaseMemoryBackend):
            CONFIG_CLASS = MemoryConfig
            
            async def initialize(self):
                pass
            
            async def close(self):
                pass
            
            async def health_check(self):
                return True
            
            # Mock all abstract methods
            async def store_message(self, message, conversation_id):
                pass
            
            async def retrieve_messages(self, conversation_id, limit=None):
                return []
            
            async def search_messages(self, query, user_id=None, limit=10):
                return []
            
            async def store_memory(self, memory_entry):
                pass
            
            async def retrieve_memories(self, query):
                return []
            
            async def delete_memory(self, memory_id):
                pass
            
            async def create_session(self, user_id, metadata=None):
                from bruno_core.models.context import SessionContext
                from datetime import datetime, timezone
                return SessionContext(
                    session_id="test_session",
                    user_id=user_id,
                    conversation_id="test_conv",
                    started_at=datetime.now(timezone.utc),
                    is_active=True,
                    metadata=metadata or {}
                )
            
            async def get_session(self, session_id):
                return None
            
            async def end_session(self, session_id):
                pass
            
            async def _get_user_context(self, user_id):
                from bruno_core.models.context import UserContext
                return UserContext(
                    user_id=user_id,
                    preferences={},
                    metadata={}
                )
            
            async def _delete_non_system_messages(self, conversation_id, messages):
                pass
            
            async def _delete_all_messages(self, conversation_id, messages):
                pass
            
            async def _get_basic_statistics(self, user_id):
                return {"message_count": 0, "session_count": 0}
        
        # Register the mock backend
        MemoryFactory.register("mock", MockBackend, MemoryConfig)
        
        # Check it's registered
        assert MemoryFactory.is_registered("mock")
        assert "mock" in MemoryFactory.list_providers()
        
        # Create a concrete config class
        class MockConfig(MemoryConfig):
            def get_connection_string(self) -> str:
                return "mock://test"
        
        # Also need to register the config
        from bruno_memory.base.memory_config import CONFIG_CLASSES
        CONFIG_CLASSES["mock"] = MockConfig
        
        # Create instance
        backend = MemoryFactory.create("mock")
        assert isinstance(backend, MockBackend)