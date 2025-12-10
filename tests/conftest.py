"""Test configuration for pytest."""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator

from bruno_memory.factory import MemoryFactory
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
    backend = MemoryFactory.create_sqlite(database_path=temp_db_path)
    
    await backend.connect()
    
    yield backend
    
    await backend.disconnect()


@pytest.fixture
def sample_message():
    """Create a sample message for testing."""
    from bruno_core.models import Message
    from datetime import datetime
    
    return Message(
        id="test-msg-1",
        conversation_id="test-conv-1", 
        role="user",
        content="Hello, world!",
        timestamp=datetime.now(),
        user_id="test-user-1"
    )


@pytest.fixture
def sample_memory_entry():
    """Create a sample memory entry for testing."""
    from bruno_core.models import MemoryEntry, MemoryType
    from datetime import datetime
    
    return MemoryEntry(
        id="test-memory-1",
        content="This is a test memory",
        memory_type=MemoryType.EPISODIC,
        importance=0.8,
        timestamp=datetime.now(),
        user_id="test-user-1",
        conversation_id="test-conv-1",
        tags=["test", "memory"]
    )