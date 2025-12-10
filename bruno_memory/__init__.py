"""
bruno-memory: Memory storage and retrieval system for Bruno AI Platform.

This package provides multiple backend implementations for conversation history,
user context, and semantic memory management. All backends implement bruno-core's
MemoryInterface for seamless integration.

Available Backends:
    - SQLiteBackend: Local file-based storage (development, single-user)
    - PostgreSQLBackend: Production database with pgvector support
    - RedisBackend: Fast in-memory caching and session management
    - ChromaDBBackend: Vector database for semantic search
    - QdrantBackend: Advanced vector database with hybrid search

Example:
    >>> from bruno_memory import MemoryFactory
    >>> memory = MemoryFactory.create("sqlite", {"database": "conversations.db"})
    >>> await memory.store_message(message, conversation_id="conv_123")
    >>> messages = await memory.retrieve_messages("conv_123", limit=10)

See Also:
    - bruno-core: https://github.com/meggy-ai/bruno-core
    - bruno-llm: https://github.com/meggy-ai/bruno-llm
"""

from bruno_memory.__version__ import (
    __author__,
    __description__,
    __email__,
    __license__,
    __version__,
)

# Factory will be imported once implemented
# from bruno_memory.factory import MemoryFactory

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__description__",
    # "MemoryFactory",
]
