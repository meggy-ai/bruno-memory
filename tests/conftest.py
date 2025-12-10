"""Test configuration and fixtures for bruno-memory tests."""

import asyncio
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import AsyncGenerator, Dict, Any

from bruno_memory import MemoryFactory
from bruno_memory.base import BaseMemoryBackend


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
async def sqlite_backend(temp_dir) -> AsyncGenerator[BaseMemoryBackend, None]:
    """Create a SQLite backend for testing."""
    config = {
        "database_path": str(temp_dir / "test.db"),
        "enable_fts": True,
    }
    
    try:
        backend = MemoryFactory.create("sqlite", config)
        await backend.initialize()
        yield backend
    except ImportError:
        pytest.skip("SQLite backend not available")
    finally:
        if 'backend' in locals():
            await backend.close()


@pytest.fixture
async def postgresql_backend() -> AsyncGenerator[BaseMemoryBackend, None]:
    """Create a PostgreSQL backend for testing."""
    config = {
        "host": "localhost",
        "port": 5432,
        "database": "bruno_memory_test",
        "username": "postgres",
        "password": "test",
    }
    
    try:
        backend = MemoryFactory.create("postgresql", config)
        await backend.initialize()
        yield backend
    except (ImportError, Exception):
        pytest.skip("PostgreSQL backend not available or connection failed")
    finally:
        if 'backend' in locals():
            await backend.close()


@pytest.fixture
async def redis_backend() -> AsyncGenerator[BaseMemoryBackend, None]:
    """Create a Redis backend for testing."""
    config = {
        "host": "localhost",
        "port": 6379,
        "db": 15,  # Use separate test database
        "ttl_seconds": 3600,
    }
    
    try:
        backend = MemoryFactory.create("redis", config)
        await backend.initialize()
        yield backend
    except (ImportError, Exception):
        pytest.skip("Redis backend not available or connection failed")
    finally:
        if 'backend' in locals():
            await backend.close()


@pytest.fixture
async def chromadb_backend(temp_dir) -> AsyncGenerator[BaseMemoryBackend, None]:
    """Create a ChromaDB backend for testing."""
    config = {
        "persist_directory": str(temp_dir / "chroma_test"),
        "collection_name": "test_collection",
    }
    
    try:
        backend = MemoryFactory.create("chromadb", config)
        await backend.initialize()
        yield backend
    except ImportError:
        pytest.skip("ChromaDB backend not available")
    finally:
        if 'backend' in locals():
            await backend.close()


@pytest.fixture
async def qdrant_backend() -> AsyncGenerator[BaseMemoryBackend, None]:
    """Create a Qdrant backend for testing."""
    config = {
        "host": "localhost",
        "port": 6333,
        "collection_name": "test_collection",
    }
    
    try:
        backend = MemoryFactory.create("qdrant", config)
        await backend.initialize()
        yield backend
    except (ImportError, Exception):
        pytest.skip("Qdrant backend not available or connection failed")
    finally:
        if 'backend' in locals():
            await backend.close()


@pytest.fixture(params=["sqlite"])  # Add more backends as they're implemented
async def memory_backend(request, temp_dir) -> AsyncGenerator[BaseMemoryBackend, None]:
    """Parametrized fixture that tests against multiple backends."""
    backend_type = request.param
    
    if backend_type == "sqlite":
        config = {
            "database_path": str(temp_dir / "test.db"),
            "enable_fts": True,
        }
    else:
        pytest.skip(f"Backend {backend_type} not implemented yet")
    
    try:
        backend = MemoryFactory.create(backend_type, config)
        await backend.initialize()
        yield backend
    except ImportError:
        pytest.skip(f"{backend_type} backend not available")
    finally:
        if 'backend' in locals():
            await backend.close()


# Test data fixtures
@pytest.fixture
def sample_message_data():
    """Sample message data for testing."""
    from bruno_core.models.message import Message, MessageRole
    from datetime import datetime, timezone
    
    return {
        "id": "msg_123",
        "role": MessageRole.USER,
        "content": "Hello, how are you?",
        "timestamp": datetime.now(timezone.utc),
        "conversation_id": "conv_456",
        "metadata": {"source": "test"},
    }


@pytest.fixture
def sample_memory_data():
    """Sample memory entry data for testing."""
    from bruno_core.models.memory import MemoryEntry
    from datetime import datetime, timezone
    
    return {
        "id": "mem_123",
        "content": "User likes coffee in the morning",
        "user_id": "user_456", 
        "conversation_id": "conv_789",
        "created_at": datetime.now(timezone.utc),
        "metadata": {"category": "preference"},
    }


@pytest.fixture
def sample_session_data():
    """Sample session data for testing."""
    return {
        "user_id": "user_123",
        "metadata": {
            "client": "test_client",
            "version": "1.0.0"
        }
    }