"""Tests for MemoryFactory."""

import pytest
from bruno_memory.factory import MemoryFactory
from bruno_memory.exceptions import BackendNotFoundError, ConfigurationError
from bruno_memory.backends.sqlite import SQLiteMemoryBackend


class TestMemoryFactory:
    """Test cases for MemoryFactory."""
    
    def test_get_backend_names(self):
        """Test getting available backend names."""
        names = MemoryFactory.get_backend_names()
        assert "sqlite" in names
        assert isinstance(names, list)
    
    def test_create_sqlite_backend(self, temp_db_path):
        """Test creating SQLite backend."""
        backend = MemoryFactory.create_sqlite(database_path=temp_db_path)
        
        assert isinstance(backend, SQLiteMemoryBackend)
        assert backend.config.database_path == temp_db_path
    
    def test_create_backend_with_config_dict(self, temp_db_path):
        """Test creating backend with config dictionary."""
        config = {"database_path": temp_db_path}
        backend = MemoryFactory.create_backend("sqlite", config)
        
        assert isinstance(backend, SQLiteMemoryBackend)
        assert backend.config.database_path == temp_db_path
    
    def test_create_backend_with_kwargs(self, temp_db_path):
        """Test creating backend with kwargs."""
        backend = MemoryFactory.create_backend(
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
            MemoryFactory.create_backend("unknown_backend")
    
    def test_create_backend_invalid_config(self):
        """Test creating backend with invalid configuration."""
        with pytest.raises(ConfigurationError):
            MemoryFactory.create_backend("sqlite", {"invalid_param": "value"})
    
    def test_register_backend(self):
        """Test registering a new backend."""
        class DummyBackend:
            def __init__(self, config):
                pass
        
        MemoryFactory.register_backend("dummy", DummyBackend)
        
        assert "dummy" in MemoryFactory.get_backend_names()
        
        # Clean up
        del MemoryFactory._backends["dummy"]