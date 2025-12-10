# bruno-memory

**Memory storage and retrieval system for the Bruno AI Platform**

bruno-memory provides production-ready memory backend implementations for the [bruno-core](https://github.com/meggy-ai/bruno-core) framework. Store and retrieve conversation history, manage user context, and perform semantic search across multiple storage backends through a unified interface.

---

## ✨ Features

### Core Capabilities
- 🔌 **Unified Interface**: All backends implement `MemoryInterface` from bruno-core
- ⚡ **Multiple Backends**: SQLite, PostgreSQL, Redis, ChromaDB, Qdrant
- 🔄 **Async-First**: Built on asyncio for non-blocking I/O
- 🏭 **Factory Pattern**: Easy backend instantiation and configuration
- 🧠 **Smart Context**: Intelligent context window management with multiple strategies
- 🔍 **Semantic Search**: Vector-based similarity search (ChromaDB, Qdrant)

### Advanced Features
- 💾 **Multi-Level Caching**: In-memory and Redis caching for performance
- 📦 **Conversation Management**: Session lifecycle, turn-taking, branching
- 🗜️ **Memory Compression**: Automatic summarization using bruno-llm
- 🎯 **Context Strategies**: Sliding window, semantic relevance, importance-based
- 📊 **Analytics**: Track memory usage, conversation patterns, costs
- 🔐 **Privacy & Security**: Encryption at rest, data anonymization, GDPR compliance
- 🔄 **Migration Support**: Schema versioning and data migration tools

---

## 🚀 Quick Start

### Installation

```bash
# Basic installation (SQLite only)
pip install bruno-memory

# With PostgreSQL support
pip install bruno-memory[postgresql]

# With Redis caching
pip install bruno-memory[redis]

# With vector databases
pip install bruno-memory[vector]

# With embeddings support
pip install bruno-memory[embeddings]

# All backends
pip install bruno-memory[all]
```

### Basic Usage

```python
from bruno_memory import MemoryFactory
from bruno_core.models import Message, MessageRole

# Create a SQLite backend (simplest, no setup)
memory = MemoryFactory.create("sqlite", {"database": "conversations.db"})

# Store a message
message = Message(role=MessageRole.USER, content="Hello, Bruno!")
await memory.store_message(message, conversation_id="conv_123")

# Retrieve conversation history
messages = await memory.retrieve_messages("conv_123", limit=10)

# Search across conversations
results = await memory.search_messages(
    query="timer",
    user_id="user_456",
    limit=5
)
```

### Using PostgreSQL (Production)

```python
memory = MemoryFactory.create("postgresql", {
    "host": "localhost",
    "port": 5432,
    "database": "bruno_memory",
    "user": "bruno",
    "password": "secure_password"
})
```

### Using Redis (Caching)

```python
# Fast in-memory caching with optional persistence
memory = MemoryFactory.create("redis", {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "ttl": 3600  # 1 hour expiration
})
```

### Semantic Search with Vector Databases

```python
from bruno_memory import MemoryFactory
from bruno_llm import LLMFactory

# Create embedding provider
llm = LLMFactory.create("openai", {"api_key": "sk-..."})

# Create vector backend
memory = MemoryFactory.create("chromadb", {
    "persist_directory": "./chroma_data",
    "embedding_provider": llm
})

# Store with automatic embedding
await memory.store_message(message, conversation_id="conv_123")

# Semantic search
similar = await memory.search_memories(
    user_id="user_123",
    query="Tell me about music preferences",
    limit=5
)
```

---

## 📦 Supported Backends

### SQLite
**Best for:** Development, single-user applications, simple deployments

- ✅ No external dependencies
- ✅ File-based storage
- ✅ Full-text search
- ✅ Fast for small-to-medium datasets
- ❌ Limited concurrent writes

### PostgreSQL
**Best for:** Production, multi-user applications, scalable deployments

- ✅ Production-grade reliability
- ✅ Advanced querying (JSON, full-text)
- ✅ pgvector for similarity search
- ✅ Excellent concurrency support
- ✅ ACID compliance

### Redis
**Best for:** High-speed caching, session management, real-time applications

- ✅ In-memory performance
- ✅ TTL-based expiration
- ✅ Pub/sub for real-time updates
- ✅ Cluster support
- ❌ Limited by RAM

### ChromaDB
**Best for:** Semantic search, RAG applications, small-to-medium datasets

- ✅ Easy setup
- ✅ Built-in embeddings
- ✅ Metadata filtering
- ✅ Local or client-server

### Qdrant
**Best for:** Large-scale semantic search, production vector workloads

- ✅ High performance
- ✅ Hybrid search (vector + metadata)
- ✅ Distributed deployment
- ✅ Rich filtering

---

## 🏗️ Architecture

```
bruno-memory/
├── backends/          # Storage implementations
│   ├── sqlite/       # Local file-based
│   ├── postgresql/   # Production database
│   ├── redis/        # In-memory cache
│   └── vector/       # ChromaDB, Qdrant
├── managers/         # Memory management
│   ├── conversation  # Session management
│   ├── context       # Context building
│   ├── retriever     # Memory search
│   ├── compressor    # Summarization
│   └── embedding     # Vector management
└── utils/            # Utilities
    ├── cache         # Multi-level caching
    ├── migration     # Schema migrations
    ├── backup        # Export/import
    └── analytics     # Usage tracking
```

---

## 📚 Documentation

- [Quick Start Guide](docs/guides/quick_start.md)
- [Backend Selection Guide](docs/guides/backends.md)
- [Context Management](docs/guides/context_management.md)
- [Semantic Search](docs/guides/semantic_search.md)
- [API Reference](docs/api/)

---

## 🧪 Testing

```bash
# Install dev dependencies
pip install bruno-memory[dev]

# Run tests
pytest

# With coverage
pytest --cov=bruno_memory --cov-report=html

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
pytest tests/benchmarks/
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/meggy-ai/bruno-memory.git
cd bruno-memory

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev,all]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

---

## 📋 Requirements

- Python 3.10+
- bruno-core >= 0.1.0
- Backend-specific dependencies (optional)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🔗 Related Projects

- **[bruno-core](https://github.com/meggy-ai/bruno-core)**: Core interfaces and base implementations
- **[bruno-llm](https://github.com/meggy-ai/bruno-llm)**: LLM provider implementations
- **[bruno-abilities](https://github.com/meggy-ai/bruno-abilities)**: Action execution system
- **[bruno-pa](https://github.com/meggy-ai/bruno-pa)**: Personal assistant application

---

## 📮 Support

- 🐛 [Report bugs](https://github.com/meggy-ai/bruno-memory/issues)
- 💡 [Request features](https://github.com/meggy-ai/bruno-memory/issues)
- 💬 [Discussions](https://github.com/meggy-ai/bruno-memory/discussions)

---

## 🗺️ Roadmap

### v0.1.0 (Current)
- ✅ SQLite backend
- ✅ PostgreSQL backend
- ✅ Redis backend
- ✅ Basic memory management
- ✅ Context building

### v0.2.0 (Planned)
- 🔜 ChromaDB integration
- 🔜 Qdrant integration
- 🔜 Semantic search
- 🔜 Memory compression

### v0.3.0 (Future)
- 🔮 Advanced analytics
- 🔮 Privacy features
- 🔮 Performance optimizations

---

**Made with ❤️ by the Meggy AI team**
