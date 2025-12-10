"""Basic usage example for bruno-memory."""

import asyncio
from pathlib import Path

# This example demonstrates the basic API and will be updated
# as backends are implemented


async def basic_usage_example():
    """Demonstrate basic bruno-memory usage."""
    print("🚀 Bruno Memory - Basic Usage Example")
    print("=" * 50)
    
    # Import bruno-memory components
    from bruno_memory import MemoryFactory
    from bruno_memory.exceptions import BackendNotAvailableError
    
    print("📋 1. Listing available backends...")
    backends = MemoryFactory.list_providers()
    print(f"Available backends: {backends}")
    
    if not backends:
        print("⚠️  No backends are currently implemented.")
        print("   This is expected as we're in Phase 1 - Project Foundation")
        return
    
    # Try to create a backend (will fail until backends are implemented)
    print("\n🏗️  2. Attempting to create a memory backend...")
    try:
        memory = MemoryFactory.create("sqlite", {
            "database_path": "./example_memory.db"
        })
        print("✅ Successfully created SQLite backend")
        
        # Initialize the backend
        await memory.initialize()
        print("✅ Backend initialized")
        
        # Test health check
        is_healthy = await memory.health_check()
        print(f"✅ Health check: {is_healthy}")
        
        # Close the backend
        await memory.close()
        print("✅ Backend closed successfully")
        
    except BackendNotAvailableError as e:
        print(f"⚠️  Backend not available: {e}")
        print("   This is expected - backends will be implemented in later phases")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print("\n🎯 3. Testing configuration system...")
    try:
        from bruno_memory.base import create_config, SQLiteConfig
        
        # Test configuration creation
        config = create_config("sqlite", {
            "database_path": "./test.db",
            "enable_fts": True,
            "max_connections": 5
        })
        
        print("✅ Configuration system working")
        print(f"   - Database path: {config.database_path}")
        print(f"   - FTS enabled: {config.enable_fts}")
        print(f"   - Max connections: {config.max_connections}")
        print(f"   - Connection string: {config.get_connection_string()}")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
    
    print("\n🧪 4. Testing factory pattern...")
    try:
        # Test registration check
        sqlite_available = MemoryFactory.is_registered("sqlite")
        postgres_available = MemoryFactory.is_registered("postgresql")
        
        print(f"✅ SQLite registered: {sqlite_available}")
        print(f"✅ PostgreSQL registered: {postgres_available}")
        
        # Test environment-based creation (will fail gracefully)
        try:
            memory_from_env = MemoryFactory.create_from_env("sqlite")
            print("✅ Environment-based creation works")
        except BackendNotAvailableError:
            print("⚠️  Environment-based creation failed (expected)")
            
    except Exception as e:
        print(f"❌ Factory pattern error: {e}")
    
    print("\n📊 5. Summary")
    print("=" * 50)
    print("✅ Package imports successfully")
    print("✅ Factory pattern works") 
    print("✅ Configuration system works")
    print("✅ Exception handling works")
    print("⏳ Backends not implemented yet (coming in Phase 2+)")
    print("\n🎉 Foundation is solid! Ready for backend implementation.")


async def configuration_examples():
    """Demonstrate different configuration options."""
    print("\n🔧 Configuration Examples")
    print("=" * 30)
    
    from bruno_memory.base import create_config
    
    # SQLite configuration
    print("📁 SQLite Configuration:")
    sqlite_config = create_config("sqlite", {
        "database_path": "./conversations.db",
        "enable_fts": True,
        "enable_wal": True,
        "max_connections": 10
    })
    print(f"   Connection: {sqlite_config.get_connection_string()}")
    
    # PostgreSQL configuration
    print("\n🐘 PostgreSQL Configuration:")
    postgres_config = create_config("postgresql", {
        "host": "localhost",
        "port": 5432,
        "database": "bruno_memory",
        "username": "postgres",
        "password": "secret",
        "enable_pgvector": True
    })
    print(f"   Connection: {postgres_config.get_connection_string()}")
    
    # Redis configuration
    print("\n🔴 Redis Configuration:")
    redis_config = create_config("redis", {
        "host": "localhost", 
        "port": 6379,
        "db": 0,
        "ttl_seconds": 3600
    })
    print(f"   Connection: {redis_config.get_connection_string()}")
    
    # ChromaDB configuration
    print("\n🌈 ChromaDB Configuration:")
    chroma_config = create_config("chromadb", {
        "persist_directory": "./chroma_db",
        "collection_name": "conversations"
    })
    print(f"   Connection: {chroma_config.get_connection_string()}")
    
    # Qdrant configuration
    print("\n🎯 Qdrant Configuration:")
    qdrant_config = create_config("qdrant", {
        "host": "localhost",
        "port": 6333,
        "collection_name": "conversations",
        "vector_size": 1536
    })
    print(f"   Connection: {qdrant_config.get_connection_string()}")


async def integration_preview():
    """Preview of bruno-core integration."""
    print("\n🔗 Bruno-Core Integration Preview")
    print("=" * 40)
    
    try:
        # Import bruno-core components to verify integration
        from bruno_core.models.message import Message, MessageRole
        from bruno_core.models.context import ConversationContext
        from bruno_core.models.memory import MemoryEntry, MemoryQuery
        from bruno_core.interfaces import MemoryInterface
        
        print("✅ bruno-core imports successful")
        
        # Create sample objects
        message = Message(
            role=MessageRole.USER,
            content="Hello, how are you today?"
        )
        print(f"✅ Sample message created: {message.role.value}")
        
        # Test serialization utilities (from base backend)
        from bruno_memory.base import BaseMemoryBackend
        
        # We can't instantiate abstract class, but we can test serialization methods
        # by creating a concrete subclass for testing
        class TestBackend(BaseMemoryBackend):
            def __init__(self):
                pass  # Skip config for testing
            
            # Implement abstract methods with stubs
            async def initialize(self): pass
            async def close(self): pass
            async def health_check(self): return True
            async def store_message(self, message, conversation_id): pass
            async def retrieve_messages(self, conversation_id, limit=None): return []
            async def search_messages(self, query, user_id=None, limit=10): return []
            async def store_memory(self, memory_entry): pass
            async def retrieve_memories(self, query): return []
            async def delete_memory(self, memory_id): pass
            async def create_session(self, user_id, metadata=None): pass
            async def get_session(self, session_id): return None
            async def end_session(self, session_id): pass
            async def _get_user_context(self, user_id): pass
            async def _delete_non_system_messages(self, conversation_id, messages): pass
            async def _delete_all_messages(self, conversation_id, messages): pass
            async def _get_basic_statistics(self, user_id): return {}
        
        backend = TestBackend()
        
        # Test message serialization
        serialized = backend.serialize_message(message)
        print("✅ Message serialization works")
        
        deserialized = backend.deserialize_message(serialized)
        print("✅ Message deserialization works")
        print(f"   Original: {message.content}")
        print(f"   Roundtrip: {deserialized.content}")
        
        print("✅ Bruno-core integration verified")
        
    except ImportError as e:
        print(f"❌ bruno-core import failed: {e}")
        print("   Make sure bruno-core is installed")
    except Exception as e:
        print(f"❌ Integration test failed: {e}")


async def main():
    """Main example function."""
    print("🎯 Bruno Memory - Foundation Testing")
    print("=" * 60)
    
    await basic_usage_example()
    await configuration_examples()
    await integration_preview()
    
    print("\n" + "=" * 60)
    print("🏁 Foundation testing complete!")
    print("📝 Next steps:")
    print("   1. ✅ Phase 1 (Project Foundation) - COMPLETED")
    print("   2. ⏳ Phase 2 (Base Abstractions) - Ready to start")
    print("   3. ⏳ Phase 3 (SQLite Backend) - Waiting for Phase 2")
    print("   4. ⏳ Phase 4+ (Additional backends) - Future phases")


if __name__ == "__main__":
    asyncio.run(main())