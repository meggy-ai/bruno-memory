"""
Unit tests for configuration models.

Tests configuration validation and creation.
"""

import pytest
from pydantic import ValidationError

from bruno_memory.base.memory_config import (
    ChromaDBConfig,
    CompressionConfig,
    EmbeddingConfig,
    PostgreSQLConfig,
    QdrantConfig,
    RedisConfig,
    SQLiteConfig,
    create_backend_config,
)


class TestSQLiteConfig:
    """Test SQLite configuration."""

    def test_default_config(self):
        """Test default SQLite configuration."""
        config = SQLiteConfig()
        assert config.database == "bruno_memory.db"
        assert config.journal_mode == "WAL"
        assert config.synchronous == "NORMAL"
        assert config.timeout == 30.0

    def test_custom_config(self):
        """Test custom SQLite configuration."""
        config = SQLiteConfig(database=":memory:", journal_mode="DELETE")
        assert config.database == ":memory:"
        assert config.journal_mode == "DELETE"

    def test_invalid_journal_mode(self):
        """Test invalid journal mode."""
        with pytest.raises(ValidationError):
            SQLiteConfig(journal_mode="INVALID")

    def test_invalid_synchronous(self):
        """Test invalid synchronous mode."""
        with pytest.raises(ValidationError):
            SQLiteConfig(synchronous="INVALID")


class TestPostgreSQLConfig:
    """Test PostgreSQL configuration."""

    def test_default_config(self):
        """Test default PostgreSQL configuration."""
        config = PostgreSQLConfig()
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.database == "bruno_memory"
        assert config.user == "postgres"
        assert config.min_pool_size == 1
        assert config.max_pool_size == 10

    def test_custom_config(self):
        """Test custom PostgreSQL configuration."""
        config = PostgreSQLConfig(
            host="db.example.com",
            port=5433,
            database="custom_db",
            user="custom_user",
            password="secret123",
        )
        assert config.host == "db.example.com"
        assert config.port == 5433
        assert config.database == "custom_db"
        assert config.user == "custom_user"
        assert config.password.get_secret_value() == "secret123"

    def test_invalid_port(self):
        """Test invalid port number."""
        with pytest.raises(ValidationError):
            PostgreSQLConfig(port=99999)

    def test_invalid_pool_size(self):
        """Test invalid pool size relationship."""
        with pytest.raises(ValidationError):
            PostgreSQLConfig(min_pool_size=10, max_pool_size=5)

    def test_invalid_ssl_mode(self):
        """Test invalid SSL mode."""
        with pytest.raises(ValidationError):
            PostgreSQLConfig(ssl_mode="invalid")


class TestRedisConfig:
    """Test Redis configuration."""

    def test_default_config(self):
        """Test default Redis configuration."""
        config = RedisConfig()
        assert config.host == "localhost"
        assert config.port == 6379
        assert config.db == 0
        assert config.ttl == 3600
        assert config.key_prefix == "bruno:"

    def test_custom_config(self):
        """Test custom Redis configuration."""
        config = RedisConfig(
            host="redis.example.com",
            port=6380,
            db=1,
            password="secret",
            ttl=7200,
            key_prefix="test:",
        )
        assert config.host == "redis.example.com"
        assert config.port == 6380
        assert config.db == 1
        assert config.password.get_secret_value() == "secret"
        assert config.ttl == 7200
        assert config.key_prefix == "test:"

    def test_invalid_db_number(self):
        """Test invalid database number."""
        with pytest.raises(ValidationError):
            RedisConfig(db=20)

    def test_ssl_config(self):
        """Test SSL configuration."""
        config = RedisConfig(ssl=True)
        assert config.ssl is True


class TestChromaDBConfig:
    """Test ChromaDB configuration."""

    def test_default_config(self):
        """Test default ChromaDB configuration."""
        config = ChromaDBConfig()
        assert config.persist_directory == "./chroma_data"
        assert config.collection_name == "bruno_memory"
        assert config.distance_metric == "cosine"
        assert config.embedding_dimension == 1536

    def test_custom_config(self):
        """Test custom ChromaDB configuration."""
        config = ChromaDBConfig(
            persist_directory="/data/chroma",
            collection_name="custom_collection",
            distance_metric="l2",
            embedding_dimension=768,
        )
        assert config.persist_directory == "/data/chroma"
        assert config.collection_name == "custom_collection"
        assert config.distance_metric == "l2"
        assert config.embedding_dimension == 768

    def test_invalid_distance_metric(self):
        """Test invalid distance metric."""
        with pytest.raises(ValidationError):
            ChromaDBConfig(distance_metric="invalid")

    def test_invalid_collection_name(self):
        """Test invalid collection name."""
        with pytest.raises(ValidationError):
            ChromaDBConfig(collection_name="")

    def test_collection_name_too_long(self):
        """Test collection name too long."""
        with pytest.raises(ValidationError):
            ChromaDBConfig(collection_name="a" * 64)

    def test_client_mode_config(self):
        """Test client mode configuration."""
        config = ChromaDBConfig(host="chroma.example.com", port=8000)
        assert config.host == "chroma.example.com"
        assert config.port == 8000


class TestQdrantConfig:
    """Test Qdrant configuration."""

    def test_default_config(self):
        """Test default Qdrant configuration."""
        config = QdrantConfig()
        assert config.host == "localhost"
        assert config.port == 6333
        assert config.grpc_port == 6334
        assert config.collection_name == "bruno_memory"
        assert config.distance_metric == "Cosine"

    def test_custom_config(self):
        """Test custom Qdrant configuration."""
        config = QdrantConfig(
            host="qdrant.example.com",
            port=6335,
            api_key="secret_key",
            collection_name="custom",
            distance_metric="Euclid",
            prefer_grpc=True,
            https=True,
        )
        assert config.host == "qdrant.example.com"
        assert config.port == 6335
        assert config.api_key.get_secret_value() == "secret_key"
        assert config.collection_name == "custom"
        assert config.distance_metric == "Euclid"
        assert config.prefer_grpc is True
        assert config.https is True

    def test_invalid_distance_metric(self):
        """Test invalid distance metric."""
        with pytest.raises(ValidationError):
            QdrantConfig(distance_metric="invalid")


class TestEmbeddingConfig:
    """Test embedding configuration."""

    def test_default_config(self):
        """Test default embedding configuration."""
        config = EmbeddingConfig()
        assert config.provider == "openai"
        assert config.model == "text-embedding-ada-002"
        assert config.batch_size == 100
        assert config.cache_embeddings is True

    def test_custom_config(self):
        """Test custom embedding configuration."""
        config = EmbeddingConfig(
            provider="sentence-transformers",
            model="all-MiniLM-L6-v2",
            batch_size=50,
            cache_embeddings=False,
        )
        assert config.provider == "sentence-transformers"
        assert config.model == "all-MiniLM-L6-v2"
        assert config.batch_size == 50
        assert config.cache_embeddings is False


class TestCompressionConfig:
    """Test compression configuration."""

    def test_default_config(self):
        """Test default compression configuration."""
        config = CompressionConfig()
        assert config.enabled is True
        assert config.threshold_messages == 100
        assert config.threshold_age_days == 7
        assert config.summary_length == 500
        assert config.keep_recent == 20

    def test_custom_config(self):
        """Test custom compression configuration."""
        config = CompressionConfig(
            enabled=False,
            threshold_messages=50,
            threshold_age_days=14,
            summary_length=1000,
            keep_recent=10,
        )
        assert config.enabled is False
        assert config.threshold_messages == 50
        assert config.threshold_age_days == 14
        assert config.summary_length == 1000
        assert config.keep_recent == 10


class TestCreateBackendConfig:
    """Test create_backend_config factory function."""

    def test_create_sqlite_config(self):
        """Test creating SQLite config."""
        config = create_backend_config("sqlite", {"database": "test.db"})
        assert isinstance(config, SQLiteConfig)
        assert config.database == "test.db"

    def test_create_postgresql_config(self):
        """Test creating PostgreSQL config."""
        config = create_backend_config("postgresql", {"host": "localhost"})
        assert isinstance(config, PostgreSQLConfig)
        assert config.host == "localhost"

    def test_create_postgres_alias(self):
        """Test creating config with postgres alias."""
        config = create_backend_config("postgres", {"host": "localhost"})
        assert isinstance(config, PostgreSQLConfig)

    def test_create_redis_config(self):
        """Test creating Redis config."""
        config = create_backend_config("redis", {"port": 6380})
        assert isinstance(config, RedisConfig)
        assert config.port == 6380

    def test_create_chromadb_config(self):
        """Test creating ChromaDB config."""
        config = create_backend_config("chromadb", {"collection_name": "test"})
        assert isinstance(config, ChromaDBConfig)
        assert config.collection_name == "test"

    def test_create_chroma_alias(self):
        """Test creating config with chroma alias."""
        config = create_backend_config("chroma", {})
        assert isinstance(config, ChromaDBConfig)

    def test_create_qdrant_config(self):
        """Test creating Qdrant config."""
        config = create_backend_config("qdrant", {"host": "qdrant.local"})
        assert isinstance(config, QdrantConfig)
        assert config.host == "qdrant.local"

    def test_unknown_backend_type(self):
        """Test unknown backend type."""
        with pytest.raises(ValueError) as exc_info:
            create_backend_config("unknown", {})
        assert "Unknown backend type" in str(exc_info.value)

    def test_invalid_config_parameters(self):
        """Test invalid configuration parameters."""
        with pytest.raises(ValidationError):
            create_backend_config("sqlite", {"journal_mode": "INVALID"})
