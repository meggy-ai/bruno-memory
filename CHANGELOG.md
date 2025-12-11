# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure
- SQLite backend implementation
- PostgreSQL backend with vector support
- Redis backend for caching
- ChromaDB and Qdrant vector database backends
- Embedding management system
- Context building and retrieval
- Memory compression utilities
- Analytics and reporting
- Backup and restore functionality
- Caching layer with TTL and LRU
- Advanced memory prioritization with multi-factor scoring
- Privacy and security features (encryption, anonymization, GDPR)
- Performance monitoring and optimization tools
- Comprehensive documentation with MkDocs
- CI/CD pipeline with GitHub Actions
- Automated testing across Python 3.10, 3.11, 3.12
- Code quality tools (black, ruff, mypy)
- Security scanning and dependency auditing

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.1.0] - YYYY-MM-DD

### Added
- Initial release
- Core memory management functionality
- Multiple backend support
- Embedding integration
- Basic documentation

---

## Release Process

1. Update version in `pyproject.toml` and `bruno_memory/__init__.py`
2. Update this CHANGELOG with release date and changes
3. Commit changes: `git commit -am "Release v0.1.0"`
4. Create tag: `git tag -a v0.1.0 -m "Release version 0.1.0"`
5. Push: `git push origin main --tags`
6. GitHub Actions will automatically publish to PyPI

## Version Policy

- **Major** (X.0.0): Breaking API changes
- **Minor** (0.X.0): New features, backwards compatible
- **Patch** (0.0.X): Bug fixes, backwards compatible

## Migration Guides

### Migrating from 0.0.x to 0.1.x

[Migration guide will be added here when releasing 0.1.0]
