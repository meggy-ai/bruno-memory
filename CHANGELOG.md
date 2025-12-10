# Changelog

All notable changes to bruno-memory will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and foundation
- Project configuration (pyproject.toml)
- Custom exception hierarchy
- Documentation framework (README, CONTRIBUTING)

### In Progress
- Base abstractions for memory backends
- SQLite backend implementation
- Memory management components

---

## [0.1.0] - TBD

### Planned Features

#### Core
- SQLite backend for local storage
- PostgreSQL backend for production
- Redis backend for caching
- Factory pattern for backend creation
- bruno-core MemoryInterface implementation

#### Memory Management
- Conversation manager for session lifecycle
- Context builder with multiple strategies
- Memory retriever with hybrid search
- Basic analytics and statistics

#### Testing
- Comprehensive unit test suite
- Integration tests with bruno-core
- Performance benchmarks
- Backend-agnostic test framework

#### Documentation
- Complete API documentation
- Backend selection guide
- Quick start tutorial
- Usage examples

---

## Version History

### Version Format
- **Major.Minor.Patch** (e.g., 1.2.3)
- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

### Change Categories
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

---

## Future Roadmap

### v0.2.0 (Planned)
- ChromaDB backend
- Qdrant backend
- Semantic search capabilities
- Memory compression with bruno-llm
- Embedding management

### v0.3.0 (Future)
- Advanced memory prioritization
- Privacy and security features
- Multi-level caching
- Migration tools
- Backup and export utilities

### v0.4.0 (Future)
- Performance optimizations
- Advanced analytics
- Cost tracking integration
- Distributed deployment support

---

## Development Notes

### Breaking Changes Policy
- Major version increments indicate breaking changes
- Deprecation warnings provided for at least one minor version
- Migration guides provided for breaking changes

### Release Schedule
- Regular releases every 4-6 weeks
- Patch releases as needed for critical bugs
- Pre-release versions available for testing

---

[Unreleased]: https://github.com/meggy-ai/bruno-memory/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/meggy-ai/bruno-memory/releases/tag/v0.1.0
