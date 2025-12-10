"""Tests for MemoryBackendFactory."""

import pytest
from bruno_memory.factory import MemoryBackendFactory, create_backend, list_backends
from bruno_memory.exceptions import BackendNotFoundError, ConfigurationError
from bruno_memory.backends.sqlite import SQLiteMemoryBackend


class TestMemoryBackendFactory:
    """Test cases for MemoryBackendFactory."""
    
    def test_get_backend_names(self):
        """Test getting available backend names."""
        names = list_backends()
        assert "sqlite" in names
        assert isinstance(names, dict)
    
    def test_create_sqlite_backend(self, temp_db_path):
        """Test creating SQLite backend."""
        backend = create_backend("sqlite", database_path=temp_db_path)
        
        assert isinstance(backend, SQLiteMemoryBackend)
        assert backend.config.database_path == temp_db_path
    
    def test_create_backend_with_config_dict(self, temp_db_path):
        """Test creating backend with config dictionary."""
        backend = create_backend("sqlite", database_path=temp_db_path)
        
        assert isinstance(backend, SQLiteMemoryBackend)
        assert backend.config.database_path == temp_db_path
    
    def test_create_backend_with_kwargs(self, temp_db_path):
        """Test creating backend with kwargs."""
        backend = create_backend(
            "sqlite", 
            database_path=temp_db_path,
            enable_fts=False
        )
        
        assert isinstance(backend, SQLiteMemoryBackend)
        assert backend.config.database_path == temp_db_path
        assert backend.config.enable_fts is False
    
    def test_create_unknown_backend(self):
        """Test creating unknown backend type."""
        with pytest.raises(BackendNotFoundError):
            create_backend("unknown_backend")
    
    def test_create_backend_invalid_config(self):
        """Test creating backend with invalid configuration."""
        with pytest.raises((ConfigurationError, TypeError)):
            create_backend("sqlite", invalid_param="value")
    
    def test_register_backend(self):
        """Test registering a new backend."""
        from bruno_memory.factory import factory
        from bruno_memory.base import BaseMemoryBackend, MemoryConfig
        
        class DummyConfig(MemoryConfig):
            backend_type: str = "dummy"
        
        class DummyBackend(BaseMemoryBackend):
            async def connect(self):
                pass
            async def disconnect(self):
                pass
            async def health_check(self):
                return True
        
        factory.register_backend("dummy", DummyBackend, DummyConfig)
        
        assert "dummy" in list_backends()
        
        # Clean up
        if "dummy" in factory._backends:
            del factory._backends["dummy"]
        if "dummy" in factory._config_types:
            del factory._config_types["dummy"]