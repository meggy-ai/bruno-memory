# Contributing to bruno-memory

Thank you for your interest in contributing to bruno-memory! This guide will help you get started.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing Guidelines](#testing-guidelines)
- [Code Style](#code-style)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Adding a New Backend](#adding-a-new-backend)

---

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to info@meggy.ai.

**Expected Behavior:**
- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards others

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Virtual environment tool (venv, conda, etc.)
- Basic understanding of async Python
- Familiarity with bruno-core interfaces

### First Steps

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/bruno-memory.git
   cd bruno-memory
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/meggy-ai/bruno-memory.git
   ```

---

## Development Setup

### 1. Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Using conda
conda create -n bruno-memory python=3.10
conda activate bruno-memory
```

### 2. Install Dependencies

```bash
# Install in editable mode with all extras
pip install -e ".[dev,all]"
```

### 3. Install Pre-commit Hooks

```bash
pre-commit install
```

This will automatically run linting and formatting checks before each commit.

### 4. Verify Installation

```bash
# Run tests to ensure everything works
pytest

# Check code formatting
black --check bruno_memory tests
ruff check bruno_memory tests

# Type checking
mypy bruno_memory
```

---

## Project Structure

```
bruno-memory/
├── bruno_memory/              # Main package
│   ├── __init__.py           # Package initialization
│   ├── __version__.py        # Version info
│   ├── exceptions.py         # Custom exceptions
│   ├── factory.py            # Backend factory
│   ├── base/                 # Base implementations
│   ├── backends/             # Storage backends
│   ├── managers/             # Memory managers
│   └── utils/                # Utilities
├── tests/                    # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── benchmarks/          # Performance tests
├── examples/                 # Usage examples
├── docs/                     # Documentation
└── pyproject.toml           # Project configuration
```

---

## Development Workflow

### 1. Create a Feature Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write code following our [style guidelines](#code-style)
- Add tests for new functionality
- Update documentation as needed
- Run tests frequently: `pytest`

### 3. Commit Your Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat(backends): add ChromaDB backend support"
```

See [Commit Messages](#commit-messages) for format guidelines.

### 4. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

---

## Testing Guidelines

### Test Structure

We use pytest for testing. Tests are organized into three categories:

1. **Unit Tests** (`tests/unit/`): Test individual components in isolation
2. **Integration Tests** (`tests/integration/`): Test component interactions
3. **Benchmarks** (`tests/benchmarks/`): Performance testing

### Writing Tests

```python
import pytest
from bruno_memory.backends.sqlite import SQLiteBackend
from bruno_core.models import Message, MessageRole

@pytest.mark.asyncio
async def test_store_and_retrieve_message():
    """Test basic message storage and retrieval."""
    backend = SQLiteBackend(database=":memory:")
    
    # Create test message
    message = Message(
        role=MessageRole.USER,
        content="Test message"
    )
    
    # Store message
    await backend.store_message(message, conversation_id="test_conv")
    
    # Retrieve message
    messages = await backend.retrieve_messages("test_conv", limit=1)
    
    # Assert
    assert len(messages) == 1
    assert messages[0].content == "Test message"
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_sqlite_backend.py

# Run with coverage
pytest --cov=bruno_memory --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run with specific markers
pytest -m "not slow"
```

### Test Coverage

We aim for 85%+ test coverage. Check coverage:

```bash
pytest --cov=bruno_memory --cov-report=term-missing
```

---

## Code Style

### Formatting

We use **Black** for code formatting and **Ruff** for linting.

```bash
# Format code
black bruno_memory tests examples

# Check formatting
black --check bruno_memory tests

# Lint code
ruff check bruno_memory tests

# Fix linting issues automatically
ruff check --fix bruno_memory tests
```

### Type Hints

All public APIs must have type hints:

```python
from typing import Optional, List
from bruno_core.models import Message

async def retrieve_messages(
    self,
    conversation_id: str,
    limit: Optional[int] = None,
) -> List[Message]:
    """Retrieve messages from conversation."""
    pass
```

Run type checking:

```bash
mypy bruno_memory
```

### Docstrings

Use Google-style docstrings:

```python
def store_message(self, message: Message, conversation_id: str) -> None:
    """
    Store a message in the backend.

    Args:
        message: Message to store
        conversation_id: ID of the conversation

    Raises:
        StorageError: If storage fails

    Example:
        >>> backend = SQLiteBackend()
        >>> await backend.store_message(message, "conv_123")
    """
    pass
```

### Naming Conventions

- **Classes**: PascalCase (`SQLiteBackend`, `MemoryFactory`)
- **Functions/Methods**: snake_case (`store_message`, `retrieve_context`)
- **Constants**: UPPER_SNAKE_CASE (`DEFAULT_TIMEOUT`, `MAX_RETRIES`)
- **Private methods**: Leading underscore (`_serialize_message`)

---

## Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
type(scope): brief description

Detailed explanation if needed.

- Bullet point 1
- Bullet point 2

Refs: #123
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

### Examples

```
feat(backends): add ChromaDB backend support

Implement ChromaDB backend with full MemoryInterface support.
Includes embedding generation and similarity search.

- Add ChromaDBBackend class
- Add configuration model
- Add integration tests

Refs: #45
```

```
fix(sqlite): handle concurrent write errors

Add proper locking for SQLite concurrent writes to prevent
database locked errors in multi-threaded scenarios.

Refs: #67
```

---

## Pull Request Process

### Before Submitting

1. ✅ All tests pass locally
2. ✅ Code is formatted (black, ruff)
3. ✅ Type hints are complete (mypy passes)
4. ✅ Documentation is updated
5. ✅ CHANGELOG.md is updated (if applicable)
6. ✅ Commits follow conventional format

### PR Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass locally

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. Automated checks run (CI/CD)
2. At least one maintainer review required
3. Address feedback and update PR
4. Once approved, maintainer will merge

---

## Adding a New Backend

### 1. Create Backend Directory

```bash
mkdir -p bruno_memory/backends/mybackend
touch bruno_memory/backends/mybackend/__init__.py
touch bruno_memory/backends/mybackend/backend.py
touch bruno_memory/backends/mybackend/config.py
```

### 2. Implement MemoryInterface

```python
# bruno_memory/backends/mybackend/backend.py
from bruno_core.interfaces import MemoryInterface
from bruno_core.models import Message
from typing import List, Optional

class MyBackend(MemoryInterface):
    """My custom backend implementation."""
    
    async def store_message(
        self,
        message: Message,
        conversation_id: str,
    ) -> None:
        """Store a message."""
        # Implementation
        pass
    
    async def retrieve_messages(
        self,
        conversation_id: str,
        limit: Optional[int] = None,
    ) -> List[Message]:
        """Retrieve messages."""
        # Implementation
        pass
    
    # ... implement all other MemoryInterface methods
```

### 3. Create Configuration Model

```python
# bruno_memory/backends/mybackend/config.py
from pydantic import BaseModel, Field

class MyBackendConfig(BaseModel):
    """Configuration for MyBackend."""
    
    host: str = Field(default="localhost")
    port: int = Field(default=5000)
    timeout: float = Field(default=30.0)
```

### 4. Add Tests

```python
# tests/unit/test_mybackend.py
import pytest
from bruno_memory.backends.mybackend import MyBackend

@pytest.mark.asyncio
async def test_mybackend_store_message():
    backend = MyBackend()
    # Test implementation
```

### 5. Register in Factory

Update `pyproject.toml`:

```toml
[project.entry-points."bruno.memory_backends"]
mybackend = "bruno_memory.backends.mybackend:MyBackend"
```

### 6. Add Documentation

Create `docs/guides/mybackend.md` with usage guide.

---

## Questions?

- 💬 [Open a discussion](https://github.com/meggy-ai/bruno-memory/discussions)
- 🐛 [Report a bug](https://github.com/meggy-ai/bruno-memory/issues)
- 📧 Email: info@meggy.ai

---

Thank you for contributing to bruno-memory! 🎉
