"""Unit tests for memory configuration classes."""

import pytest
from pathlib import Path
from unittest.mock import patch

from bruno_memory.base.memory_config import (
    SQLiteConfig,
    PostgreSQLConfig,
    RedisConfig, 
    ChromaDBConfig,
    QdrantConfig,
    create_config,
)


class TestSQLiteConfig:
    """Test SQLite configuration."""
    
    def test_default_config(self):
        """Test default SQLite configuration."""
        config = SQLiteConfig()
        
        assert config.database_path is not None
        assert config.enable_wal is True
        assert config.enable_fts is True
        assert config.max_connections == 10
        assert "journal_mode" in config.pragma_settings
    
    def test_custom_database_path(self, tmp_path):
        """Test custom database path."""
        db_path = tmp_path / "custom.db"
        config = SQLiteConfig(database_path=str(db_path))
        
        assert Path(config.database_path) == db_path.resolve()
    
    def test_connection_string(self):
        """Test SQLite connection string generation."""
        config = SQLiteConfig(database_path="./test.db")
        conn_str = config.get_connection_string()
        
        assert conn_str.startswith("sqlite:///")
        assert "test.db" in conn_str


class TestPostgreSQLConfig:
    """Test PostgreSQL configuration."""
    
    def test_default_config(self):
        """Test default PostgreSQL configuration.""" 
        config = PostgreSQLConfig()
        
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.database == "bruno_memory"
        assert config.username == "postgres"
        assert config.enable_pgvector is True
        assert config.vector_dimensions == 1536
    
    def test_custom_config(self):
        """Test custom PostgreSQL configuration."""
        config = PostgreSQLConfig(
            host="db.example.com",
            port=5433,
            database="custom_db",
            username="custom_user",
            password="secret123"
        )
        
        assert config.host == "db.example.com"
        assert config.port == 5433
        assert config.database == "custom_db"
        assert config.username == "custom_user"
        assert config.password == "secret123"
    
    def test_connection_string(self):
        """Test PostgreSQL connection string generation."""
        config = PostgreSQLConfig(
            host="localhost",
            port=5432,
            database="testdb",
            username="user",
            password="pass"
        )
        
        conn_str = config.get_connection_string()
        assert conn_str == "postgresql://user:pass@localhost:5432/testdb"
    
    def test_connection_string_no_password(self):
        """Test connection string without password."""
        config = PostgreSQLConfig(
            username="user",
            password=""
        )
        
        conn_str = config.get_connection_string()
        assert conn_str == "postgresql://user@localhost:5432/bruno_memory"
    
    def test_port_validation(self):
        """Test port validation."""
        with pytest.raises(ValueError):
            PostgreSQLConfig(port=0)  # Invalid port
        
        with pytest.raises(ValueError):
            PostgreSQLConfig(port=65536)  # Invalid port


class TestRedisConfig:
    """Test Redis configuration."""
    
    def test_default_config(self):
        """Test default Redis configuration."""
        config = RedisConfig()
        
        assert config.host == "localhost"
        assert config.port == 6379
        assert config.db == 0
        assert config.ttl_seconds == 3600
        assert config.cluster_mode is False
    
    def test_custom_config(self):
        """Test custom Redis configuration."""
        config = RedisConfig(
            host="redis.example.com",
            port=6380,
            db=1,
            password="secret",
            ttl_seconds=7200
        )
        
        assert config.host == "redis.example.com"
        assert config.port == 6380
        assert config.db == 1
        assert config.password == "secret"
        assert config.ttl_seconds == 7200
    
    def test_connection_string(self):
        """Test Redis connection string generation."""
        config = RedisConfig(password="secret", db=1)
        conn_str = config.get_connection_string()
        
        assert conn_str == "redis://:secret@localhost:6379/1"
    
    def test_connection_string_no_password(self):
        """Test connection string without password."""
        config = RedisConfig()
        conn_str = config.get_connection_string()
        
        assert conn_str == "redis://localhost:6379/0"
    
    def test_ttl_validation(self):
        """Test TTL validation."""
        with pytest.raises(ValueError):
            RedisConfig(ttl_seconds=30)  # Too low
        
        with pytest.raises(ValueError):
            RedisConfig(ttl_seconds=86400 * 8)  # Too high


class TestChromaDBConfig:
    """Test ChromaDB configuration."""
    
    def test_default_config(self):
        """Test default ChromaDB configuration."""
        config = ChromaDBConfig()
        
        assert Path(config.persist_directory).name == "chroma_db"
        assert config.collection_name == "bruno_conversations"
        assert config.distance_metric == "cosine"
        assert config.batch_size == 100
    
    def test_custom_persist_directory(self, tmp_path):
        """Test custom persist directory."""
        persist_dir = tmp_path / "custom_chroma"
        config = ChromaDBConfig(persist_directory=str(persist_dir))
        
        assert Path(config.persist_directory) == persist_dir.resolve()
        assert persist_dir.exists()  # Should be created
    
    def test_connection_string(self):
        """Test ChromaDB connection string generation."""
        config = ChromaDBConfig(persist_directory="./chroma")
        conn_str = config.get_connection_string()
        
        assert conn_str.startswith("chromadb://")
        assert "chroma" in conn_str


class TestQdrantConfig:
    """Test Qdrant configuration."""
    
    def test_default_config(self):
        """Test default Qdrant configuration."""
        config = QdrantConfig()
        
        assert config.host == "localhost"
        assert config.port == 6333
        assert config.grpc_port == 6334
        assert config.prefer_grpc is True
        assert config.collection_name == "bruno_conversations"
        assert config.vector_size == 1536
        assert config.distance_metric == "Cosine"
    
    def test_custom_config(self):
        """Test custom Qdrant configuration."""
        config = QdrantConfig(
            host="qdrant.example.com",
            port=6334,
            api_key="secret",
            collection_name="custom_collection",
            vector_size=768
        )
        
        assert config.host == "qdrant.example.com"
        assert config.port == 6334
        assert config.api_key == "secret"
        assert config.collection_name == "custom_collection"
        assert config.vector_size == 768
    
    def test_connection_string_grpc(self):
        """Test Qdrant connection string with gRPC."""
        config = QdrantConfig(prefer_grpc=True)
        conn_str = config.get_connection_string()
        
        assert conn_str == "qdrant://localhost:6334"
    
    def test_connection_string_http(self):
        """Test Qdrant connection string with HTTP."""
        config = QdrantConfig(prefer_grpc=False)
        conn_str = config.get_connection_string()
        
        assert conn_str == "qdrant://localhost:6333"


class TestConfigFactory:
    """Test configuration factory function."""
    
    def test_create_sqlite_config(self):
        """Test creating SQLite config via factory."""
        config = create_config("sqlite", {"database_path": "./test.db"})
        
        assert isinstance(config, SQLiteConfig)
        assert "test.db" in config.database_path
    
    def test_create_postgresql_config(self):
        """Test creating PostgreSQL config via factory."""
        config = create_config("postgresql", {"host": "custom.host"})
        
        assert isinstance(config, PostgreSQLConfig)
        assert config.host == "custom.host"
    
    def test_create_unknown_config(self):
        """Test creating unknown config type raises error."""
        with pytest.raises(ValueError) as exc_info:
            create_config("unknown")
        
        assert "Unknown backend type: unknown" in str(exc_info.value)
        assert "Available:" in str(exc_info.value)
    
    def test_create_config_empty_dict(self):
        """Test creating config with empty dict uses defaults."""
        config = create_config("sqlite", {})
        
        assert isinstance(config, SQLiteConfig)
        assert config.max_connections == 10  # Default value