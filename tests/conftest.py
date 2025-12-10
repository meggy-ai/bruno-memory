"""Test configuration for pytest."""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator

from bruno_memory.factory import MemoryBackendFactory
from bruno_memory.backends.sqlite import SQLiteMemoryBackend


@pytest.fixture
def temp_db_path() -> Generator[str, None, None]:
    """Create a temporary database path for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test.db"
    
    yield str(db_path)
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
async def sqlite_backend(temp_db_path: str) -> Generator[SQLiteMemoryBackend, None, None]:
    """Create a SQLite backend for testing.""" 
    from bruno_memory.base.config import SQLiteConfig
    config = SQLiteConfig(database_path=temp_db_path)
    backend = SQLiteMemoryBackend(config)
    
    await backend.connect()
    
    yield backend
    
    await backend.disconnect()


@pytest.fixture
def sample_message():
    """Create a sample message for testing."""
    from bruno_core.models import Message, MessageRole
    from datetime import datetime
    from uuid import uuid4
    
    return Message(
        id=str(uuid4()),
        conversation_id=str(uuid4()), 
        role=MessageRole.USER,
        content="Hello, world!",
        timestamp=datetime.now(),
        user_id=str(uuid4())
    )


@pytest.fixture
def sample_memory_entry():
    """Create a sample memory entry for testing."""
    from bruno_core.models import MemoryEntry, MemoryType, MemoryMetadata
    from datetime import datetime
    from uuid import uuid4
    
    return MemoryEntry(
        id=str(uuid4()),
        content="This is a test memory",
        memory_type=MemoryType.EPISODIC,
        importance=0.8,
        timestamp=datetime.now(),
        user_id=str(uuid4()),
        conversation_id=str(uuid4()),
        metadata=MemoryMetadata(),
        tags=["test", "memory"]
    )