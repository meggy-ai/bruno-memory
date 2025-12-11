# Docker Testing Environment Setup Plan
## Bruno-Memory Testing Infrastructure

**Created:** December 11, 2025  
**Project:** bruno-memory (meggy-ai platform)  
**Purpose:** Set up Docker-based testing environments for comprehensive testing of all backends

---

## 📋 Executive Summary

This plan establishes Docker-based testing environments for bruno-memory to enable complete testing of all backends (PostgreSQL, Redis, ChromaDB, Qdrant) without manual service setup. Currently, tests for external backends fail due to missing service dependencies.

### Current Issues
- ❌ PostgreSQL backend tests require running PostgreSQL instance
- ❌ Redis backend tests require running Redis instance
- ❌ Vector database tests (ChromaDB, Qdrant) need running services
- ❌ Manual service setup is error-prone and inconsistent across environments
- ❌ CI/CD pipeline cannot run full test suite

### Goals
- ✅ Automated Docker-based test environments
- ✅ One-command setup for all services
- ✅ Isolated test environments (no conflicts with local services)
- ✅ CI/CD ready configurations
- ✅ Multiple environment profiles (minimal, full, CI)
- ✅ Proper health checks and initialization

---

## 📊 Progress Tracker

### Overall Progress: 33% Complete (2/6 phases)

| Phase | Task | Status | Progress | Notes |
|-------|------|--------|----------|-------|
| 1 | Docker Compose Foundation | ✅ Completed | 100% | All compose files created |
| 2 | PostgreSQL Environment | ✅ Completed | 100% | Database with pgvector ready |
| 3 | Redis Environment | ⏳ Not Started | 0% | Cache/session setup |
| 4 | Vector Database Environments | ⏳ Not Started | 0% | ChromaDB & Qdrant |
| 5 | Testing Integration | ⏳ Not Started | 0% | Test runner updates |
| 6 | CI/CD & Documentation | ⏳ Not Started | 0% | Automation & docs |

**Legend:**
- ⏳ Not Started
- 🔄 In Progress
- ✅ Completed
- ⚠️ Blocked
- ❌ Failed

---

## 🎯 Parent Tasks and Sub-Tasks

### **Phase 1: Docker Compose Foundation** ✅ COMPLETED

**Objective:** Create base Docker Compose infrastructure with multiple environment profiles

**Sub-Tasks:**
1. ✅ Research current project structure and requirements
2. ✅ Create main `docker-compose.yml` (all services)
3. ✅ Create `docker-compose.minimal.yml` (PostgreSQL + Redis only)
4. ✅ Create `docker-compose.ci.yml` (CI/CD optimized)
5. ✅ Create `docker-compose.dev.yml` (development with volumes)
6. ✅ Create `.env.example` template for configuration
7. ✅ Create `docker/` directory structure
8. ✅ Create `.dockerignore` file

**Deliverables:**
- ✅ `docker-compose.yml` - Main compose file (all 4 services)
- ✅ `docker-compose.minimal.yml` - Minimal services (PostgreSQL + Redis)
- ✅ `docker-compose.ci.yml` - CI/CD configuration (optimized with tmpfs)
- ✅ `docker-compose.dev.yml` - Development setup (with Web UIs)
- ✅ `.env.example` - Environment variables template (comprehensive)
- ✅ `.dockerignore` - Docker ignore rules
- ✅ `docker/` directory structure with README

**Acceptance Criteria:**
- [x] All compose files are syntactically valid
- [x] Environment variables are properly templated
- [x] Services use consistent naming conventions
- [x] Health checks are defined for all services
- [x] Volumes are properly configured for data persistence

**Completion Date:** December 11, 2025

---

### **Phase 2: PostgreSQL Environment** ✅ COMPLETED

**Objective:** Set up PostgreSQL with pgvector extension for vector operations

**Sub-Tasks:**
1. ✅ Create PostgreSQL service definition in docker-compose
2. ✅ Create custom Dockerfile with pgvector extension (`docker/postgresql/Dockerfile`)
3. ✅ Create initialization SQL script (`docker/postgresql/init.sql`)
4. ✅ Create schema setup script (`docker/postgresql/setup-schema.sh`)
5. ✅ Configure PostgreSQL health checks
6. ✅ Set up PostgreSQL volume for data persistence
7. ✅ Configure PostgreSQL environment variables
8. ✅ Create PostgreSQL connection test scripts (PowerShell & Bash)
9. ✅ Update test configuration for PostgreSQL
10. ✅ Document PostgreSQL connection parameters

**Deliverables:**
- ✅ `docker/postgresql/Dockerfile` - Custom PostgreSQL 16 image with pgvector v0.5.1
- ✅ `docker/postgresql/init.sql` - Complete database schema initialization
- ✅ `docker/postgresql/setup-schema.sh` - Schema creation and verification
- ✅ `docker/postgresql/postgresql.dev.conf` - Development configuration
- ✅ `docker/postgresql/servers.json` - pgAdmin server definitions
- ✅ `docker/postgresql/dev-queries.sql` - Helpful development queries
- ✅ `scripts/test-postgres-connection.ps1` - Windows connection test
- ✅ `scripts/test-postgres-connection.sh` - Linux/Mac connection test
- ✅ `.env.test` - Test environment configuration
- ✅ Updated `pyproject.toml` - Added PostgreSQL test markers

**Acceptance Criteria:**
- [x] PostgreSQL starts successfully with pgvector
- [x] Database schema is created automatically
- [x] Health checks pass within 30 seconds
- [x] Test database is properly initialized
- [x] Connection from tests is successful
- [x] All required extensions (uuid-ossp, vector) are enabled
- [x] Test markers added to pytest configuration

**Completion Date:** December 12, 2025

---

### **Phase 3: Redis Environment** ⏳

**Objective:** Set up Redis for caching and session management

**Sub-Tasks:**
1. ⏳ Create Redis service definition in docker-compose
2. ⏳ Create Redis configuration file (`docker/redis/redis.conf`)
3. ⏳ Configure Redis health checks
4. ⏳ Set up Redis volume for data persistence (optional)
5. ⏳ Configure Redis environment variables
6. ⏳ Create Redis connection test script
7. ⏳ Update test configuration for Redis
8. ⏳ Configure Redis memory limits
9. ⏳ Set up Redis persistence strategy (if needed)
10. ⏳ Document Redis connection parameters

**Deliverables:**
- `docker/redis/redis.conf` - Redis configuration
- Redis service in compose files
- Test connection script
- Redis optimization settings

**Acceptance Criteria:**
- [ ] Redis starts successfully
- [ ] Health checks pass within 10 seconds
- [ ] Memory limits are properly configured
- [ ] Connection from tests is successful
- [ ] Redis DB 15 is available for testing

---

### **Phase 4: Vector Database Environments** ⏳

**Objective:** Set up ChromaDB and Qdrant for vector similarity search

**Sub-Tasks:**

#### ChromaDB Setup
1. ⏳ Create ChromaDB service definition
2. ⏳ Configure ChromaDB persistence volume
3. ⏳ Create ChromaDB health check
4. ⏳ Set ChromaDB environment variables
5. ⏳ Create ChromaDB connection test script
6. ⏳ Update test configuration for ChromaDB

#### Qdrant Setup
7. ⏳ Create Qdrant service definition
8. ⏳ Configure Qdrant storage volume
9. ⏳ Create Qdrant health check
10. ⏳ Set Qdrant environment variables
11. ⏳ Create Qdrant connection test script
12. ⏳ Update test configuration for Qdrant

**Deliverables:**
- ChromaDB service in compose files
- Qdrant service in compose files
- Vector DB test scripts
- Vector DB configuration documentation

**Acceptance Criteria:**
- [ ] ChromaDB starts successfully
- [ ] Qdrant starts successfully
- [ ] Both services have working health checks
- [ ] Collections can be created/queried
- [ ] Vector operations work correctly

---

### **Phase 5: Testing Integration** ⏳

**Objective:** Update test suite to work with Docker environments

**Sub-Tasks:**
1. ⏳ Create test environment setup script (`scripts/setup-test-env.sh`)
2. ⏳ Create test environment teardown script (`scripts/teardown-test-env.sh`)
3. ⏳ Update `pytest` configuration for Docker
4. ⏳ Create `tests/conftest.py` Docker fixtures
5. ⏳ Update individual test files to use Docker services
6. ⏳ Create test environment variable management
7. ⏳ Create `scripts/run-tests-docker.sh` wrapper script
8. ⏳ Update `Makefile` with Docker test targets
9. ⏳ Create test wait scripts for service readiness
10. ⏳ Add test database cleanup between test runs
11. ⏳ Create separate test configurations for each backend
12. ⏳ Implement test markers for backend-specific tests

**Deliverables:**
- `scripts/setup-test-env.sh` - Start Docker services
- `scripts/teardown-test-env.sh` - Stop and cleanup
- `scripts/run-tests-docker.sh` - Full test runner
- `scripts/wait-for-services.sh` - Health check waiter
- Updated `tests/conftest.py` - Docker-aware fixtures
- Updated `Makefile` - Docker test targets
- `.env.test` - Test environment variables

**Acceptance Criteria:**
- [ ] Tests can discover Docker services automatically
- [ ] All backend tests pass with Docker services
- [ ] Tests clean up properly after execution
- [ ] Test isolation is maintained
- [ ] Parallel test execution works
- [ ] Services start/stop reliably

---

### **Phase 6: CI/CD & Documentation** ⏳

**Objective:** Enable CI/CD testing and document the setup

**Sub-Tasks:**

#### CI/CD Integration
1. ⏳ Create GitHub Actions workflow (`.github/workflows/docker-tests.yml`)
2. ⏳ Configure Docker Compose in CI environment
3. ⏳ Set up test result reporting
4. ⏳ Configure code coverage with Docker tests
5. ⏳ Add Docker image caching for faster CI
6. ⏳ Create CI test matrix (different Python versions)

#### Documentation
7. ⏳ Create `docs/docker-testing.md` - Complete guide
8. ⏳ Update main `README.md` with Docker testing section
9. ⏳ Create `TESTING.md` - Testing guide
10. ⏳ Document troubleshooting common issues
11. ⏳ Create developer quick-start guide
12. ⏳ Add Docker architecture diagrams

#### Maintenance Scripts
13. ⏳ Create `scripts/docker-clean.sh` - Cleanup script
14. ⏳ Create `scripts/docker-logs.sh` - Log viewer
15. ⏳ Create `scripts/docker-reset.sh` - Full reset
16. ⏳ Create `scripts/check-docker-env.sh` - Validation

**Deliverables:**
- `.github/workflows/docker-tests.yml` - CI workflow
- `docs/docker-testing.md` - Complete documentation
- `TESTING.md` - Testing guide
- `scripts/docker-clean.sh` - Cleanup utilities
- Updated `README.md` - Docker instructions
- Architecture diagrams

**Acceptance Criteria:**
- [ ] CI/CD pipeline runs all tests successfully
- [ ] Documentation is clear and complete
- [ ] All scripts are tested and working
- [ ] Coverage reports are generated correctly
- [ ] Troubleshooting guide covers common issues
- [ ] New developers can set up in < 5 minutes

---

## 🛠️ Technical Specifications

### Docker Compose Service Definitions

#### PostgreSQL Service
```yaml
postgresql:
  image: postgres:16-alpine (custom with pgvector)
  ports: 5432:5432
  volumes: postgres-data:/var/lib/postgresql/data
  environment:
    - POSTGRES_DB=bruno_memory_test
    - POSTGRES_USER=postgres
    - POSTGRES_PASSWORD=testpass123
  health_check: pg_isready
```

#### Redis Service
```yaml
redis:
  image: redis:7-alpine
  ports: 6379:6379
  volumes: redis-data:/data (optional)
  command: redis-server --appendonly yes
  health_check: redis-cli ping
```

#### ChromaDB Service
```yaml
chromadb:
  image: chromadb/chroma:latest
  ports: 8000:8000
  volumes: chromadb-data:/chroma/chroma
  environment:
    - ANONYMIZED_TELEMETRY=False
  health_check: HTTP GET /api/v1/heartbeat
```

#### Qdrant Service
```yaml
qdrant:
  image: qdrant/qdrant:latest
  ports: 6333:6333, 6334:6334
  volumes: qdrant-data:/qdrant/storage
  health_check: HTTP GET /health
```

### Environment Variables

**PostgreSQL:**
- `POSTGRES_HOST=localhost`
- `POSTGRES_PORT=5432`
- `POSTGRES_USER=postgres`
- `POSTGRES_PASSWORD=testpass123`
- `POSTGRES_DB=bruno_memory_test`

**Redis:**
- `REDIS_HOST=localhost`
- `REDIS_PORT=6379`
- `REDIS_DB=15`
- `REDIS_PASSWORD=` (empty for dev/test)

**ChromaDB:**
- `CHROMADB_HOST=localhost`
- `CHROMADB_PORT=8000`

**Qdrant:**
- `QDRANT_HOST=localhost`
- `QDRANT_PORT=6333`
- `QDRANT_GRPC_PORT=6334`

### Test Configuration

**Pytest markers:**
```python
@pytest.mark.postgresql
@pytest.mark.redis
@pytest.mark.chromadb
@pytest.mark.qdrant
@pytest.mark.requires_docker
```

**Test execution modes:**
```bash
# Run all tests with Docker
make test-docker

# Run minimal backend tests only
make test-docker-minimal

# Run specific backend
make test-postgresql
make test-redis
make test-vector
```

---

## 📦 File Structure

```
bruno-memory/
├── docker/
│   ├── postgresql/
│   │   ├── Dockerfile
│   │   ├── init.sql
│   │   └── setup-schema.sh
│   ├── redis/
│   │   └── redis.conf
│   └── .dockerignore
├── scripts/
│   ├── setup-test-env.sh
│   ├── teardown-test-env.sh
│   ├── run-tests-docker.sh
│   ├── wait-for-services.sh
│   ├── docker-clean.sh
│   ├── docker-logs.sh
│   ├── docker-reset.sh
│   └── check-docker-env.sh
├── .github/
│   └── workflows/
│       └── docker-tests.yml
├── docker-compose.yml
├── docker-compose.minimal.yml
├── docker-compose.ci.yml
├── docker-compose.dev.yml
├── .env.example
├── .env.test
├── TESTING.md
└── docs/
    └── docker-testing.md
```

---

## 🚀 Quick Start (After Implementation)

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Start all services
docker-compose up -d

# 3. Wait for services to be ready
./scripts/wait-for-services.sh

# 4. Run tests
make test-docker

# 5. Stop services
docker-compose down
```

---

## ⚠️ Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Docker not installed | High | Low | Add installation check script |
| Port conflicts | Medium | Medium | Use configurable ports, document defaults |
| Slow service startup | Medium | Medium | Implement proper health checks, increase timeouts |
| Data persistence issues | Low | Low | Use named volumes, document backup procedures |
| CI/CD resource limits | Medium | Low | Optimize image sizes, use caching |
| Version compatibility | Medium | Low | Pin specific versions, test upgrades |

---

## 📈 Success Metrics

1. **Test Coverage:** Increase from X% to 95%+ (all backends tested)
2. **Setup Time:** < 5 minutes from clone to running tests
3. **Test Execution:** All tests pass consistently
4. **CI/CD:** Green builds on all PRs
5. **Developer Experience:** Positive feedback on ease of use
6. **Documentation:** Zero setup questions in first week

---

## 🔄 Iteration Plan

### Iteration 1 (Foundation)
- Phases 1-3: Basic PostgreSQL and Redis setup
- Goal: Get core backend tests running

### Iteration 2 (Vector Databases)
- Phase 4: Add ChromaDB and Qdrant
- Goal: Complete backend coverage

### Iteration 3 (Integration)
- Phase 5: Full test integration
- Goal: All tests passing with Docker

### Iteration 4 (Polish)
- Phase 6: CI/CD and documentation
- Goal: Production-ready setup

---

## 📝 Notes & Decisions

### Design Decisions
1. **Multiple Compose Files:** Allows flexible deployment scenarios
2. **Named Volumes:** Enables data persistence across restarts
3. **Health Checks:** Ensures services are ready before tests
4. **Custom PostgreSQL Image:** Required for pgvector extension
5. **Test DB 15 for Redis:** Avoids conflicts with other services
6. **Environment Variables:** All configuration via .env files

### Future Enhancements
- [ ] Add monitoring/observability stack (optional)
- [ ] Create Docker image for bruno-memory itself
- [ ] Add performance testing containers
- [ ] Create docker-compose.production.yml
- [ ] Add automatic backup scripts
- [ ] Create load testing environment

---

## 🤝 Stakeholder Sign-off

- [ ] Technical Lead Review
- [ ] QA/Testing Team Review
- [ ] DevOps Team Review
- [ ] Documentation Review

---

**Last Updated:** December 11, 2025  
**Next Review:** After Phase 3 completion  
**Document Owner:** Development Team
