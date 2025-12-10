"""
Configuration models for bruno-memory backends.

This module defines Pydantic models for backend configuration,
validation, and connection management.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, SecretStr, field_validator


class BaseBackendConfig(BaseModel):
    """
    Base configuration for all memory backends.

    Attributes:
        timeout: Operation timeout in seconds
        max_retries: Maximum retry attempts for operations
        retry_delay: Delay between retries in seconds
    """

    timeout: float = Field(default=30.0, gt=0, description="Operation timeout in seconds")
    max_retries: int = Field(default=3, ge=0, description="Maximum retry attempts")
    retry_delay: float = Field(default=1.0, ge=0, description="Delay between retries")

    model_config = {"extra": "allow"}


class SQLiteConfig(BaseBackendConfig):
    """
    Configuration for SQLite backend.

    Attributes:
        database: Path to database file or ":memory:" for in-memory
        journal_mode: SQLite journal mode (DELETE, WAL, etc.)
        synchronous: Synchronous mode (OFF, NORMAL, FULL)
        cache_size: Cache size in KB
        busy_timeout: Timeout for database locks in milliseconds
    """

    database: str = Field(
        default="bruno_memory.db", description="Database file path or :memory:"
    )
    journal_mode: str = Field(default="WAL", description="Journal mode")
    synchronous: str = Field(default="NORMAL", description="Synchronous mode")
    cache_size: int = Field(default=-2000, description="Cache size in KB (negative = KB)")
    busy_timeout: int = Field(default=5000, ge=0, description="Lock timeout in ms")

    @field_validator("journal_mode")
    @classmethod
    def validate_journal_mode(cls, v: str) -> str:
        """Validate journal mode."""
        allowed = ["DELETE", "TRUNCATE", "PERSIST", "MEMORY", "WAL", "OFF"]
        if v.upper() not in allowed:
            raise ValueError(f"Invalid journal_mode. Must be one of: {allowed}")
        return v.upper()

    @field_validator("synchronous")
    @classmethod
    def validate_synchronous(cls, v: str) -> str:
        """Validate synchronous mode."""
        allowed = ["OFF", "NORMAL", "FULL", "EXTRA"]
        if v.upper() not in allowed:
            raise ValueError(f"Invalid synchronous mode. Must be one of: {allowed}")
        return v.upper()


class PostgreSQLConfig(BaseBackendConfig):
    """
    Configuration for PostgreSQL backend.

    Attributes:
        host: Database host
        port: Database port
        database: Database name
        user: Database user
        password: Database password (stored securely)
        min_pool_size: Minimum connection pool size
        max_pool_size: Maximum connection pool size
        ssl_mode: SSL mode (disable, allow, prefer, require, verify-ca, verify-full)
        connect_timeout: Connection timeout in seconds
    """

    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, ge=1, le=65535, description="Database port")
    database: str = Field(default="bruno_memory", description="Database name")
    user: str = Field(default="postgres", description="Database user")
    password: SecretStr = Field(default=SecretStr(""), description="Database password")
    min_pool_size: int = Field(default=1, ge=1, description="Minimum pool size")
    max_pool_size: int = Field(default=10, ge=1, description="Maximum pool size")
    ssl_mode: str = Field(default="prefer", description="SSL mode")
    connect_timeout: float = Field(default=10.0, gt=0, description="Connection timeout")

    @field_validator("ssl_mode")
    @classmethod
    def validate_ssl_mode(cls, v: str) -> str:
        """Validate SSL mode."""
        allowed = ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"]
        if v.lower() not in allowed:
            raise ValueError(f"Invalid ssl_mode. Must be one of: {allowed}")
        return v.lower()

    @field_validator("max_pool_size")
    @classmethod
    def validate_pool_size(cls, v: int, info) -> int:
        """Validate pool size relationship."""
        min_size = info.data.get("min_pool_size", 1)
        if v < min_size:
            raise ValueError(f"max_pool_size must be >= min_pool_size ({min_size})")
        return v


class RedisConfig(BaseBackendConfig):
    """
    Configuration for Redis backend.

    Attributes:
        host: Redis host
        port: Redis port
        db: Database number (0-15)
        password: Redis password (stored securely)
        username: Redis username (for ACL)
        ssl: Use SSL connection
        socket_timeout: Socket timeout in seconds
        ttl: Default TTL for keys in seconds (None = no expiration)
        key_prefix: Prefix for all Redis keys
        max_connections: Maximum connection pool size
    """

    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, ge=1, le=65535, description="Redis port")
    db: int = Field(default=0, ge=0, le=15, description="Database number")
    password: Optional[SecretStr] = Field(default=None, description="Redis password")
    username: Optional[str] = Field(default=None, description="Redis username")
    ssl: bool = Field(default=False, description="Use SSL")
    socket_timeout: float = Field(default=5.0, gt=0, description="Socket timeout")
    ttl: Optional[int] = Field(default=3600, ge=0, description="Default TTL in seconds")
    key_prefix: str = Field(default="bruno:", description="Key prefix")
    max_connections: int = Field(default=50, ge=1, description="Max connections")


class ChromaDBConfig(BaseBackendConfig):
    """
    Configuration for ChromaDB backend.

    Attributes:
        persist_directory: Directory for persistent storage
        collection_name: Default collection name
        distance_metric: Distance metric (l2, ip, cosine)
        embedding_dimension: Dimension of embeddings
        host: ChromaDB server host (for client mode)
        port: ChromaDB server port (for client mode)
    """

    persist_directory: Optional[str] = Field(
        default="./chroma_data", description="Persistence directory"
    )
    collection_name: str = Field(default="bruno_memory", description="Collection name")
    distance_metric: str = Field(default="cosine", description="Distance metric")
    embedding_dimension: int = Field(default=1536, ge=1, description="Embedding dimension")
    host: Optional[str] = Field(default=None, description="ChromaDB server host")
    port: Optional[int] = Field(default=None, ge=1, le=65535, description="Server port")

    @field_validator("distance_metric")
    @classmethod
    def validate_distance_metric(cls, v: str) -> str:
        """Validate distance metric."""
        allowed = ["l2", "ip", "cosine"]
        if v.lower() not in allowed:
            raise ValueError(f"Invalid distance_metric. Must be one of: {allowed}")
        return v.lower()

    @field_validator("collection_name")
    @classmethod
    def validate_collection_name(cls, v: str) -> str:
        """Validate collection name."""
        if not v or len(v) > 63:
            raise ValueError("Collection name must be 1-63 characters")
        if not v[0].isalnum():
            raise ValueError("Collection name must start with alphanumeric character")
        return v


class QdrantConfig(BaseBackendConfig):
    """
    Configuration for Qdrant backend.

    Attributes:
        host: Qdrant server host
        port: Qdrant server port
        grpc_port: gRPC port
        api_key: API key for Qdrant Cloud (stored securely)
        collection_name: Default collection name
        distance_metric: Distance metric (cosine, euclid, dot)
        embedding_dimension: Dimension of embeddings
        prefer_grpc: Use gRPC instead of HTTP
        https: Use HTTPS
    """

    host: str = Field(default="localhost", description="Qdrant host")
    port: int = Field(default=6333, ge=1, le=65535, description="HTTP port")
    grpc_port: int = Field(default=6334, ge=1, le=65535, description="gRPC port")
    api_key: Optional[SecretStr] = Field(default=None, description="API key")
    collection_name: str = Field(default="bruno_memory", description="Collection name")
    distance_metric: str = Field(default="Cosine", description="Distance metric")
    embedding_dimension: int = Field(default=1536, ge=1, description="Embedding dimension")
    prefer_grpc: bool = Field(default=False, description="Prefer gRPC")
    https: bool = Field(default=False, description="Use HTTPS")

    @field_validator("distance_metric")
    @classmethod
    def validate_distance_metric(cls, v: str) -> str:
        """Validate distance metric."""
        allowed = ["Cosine", "Euclid", "Dot"]
        if v not in allowed:
            raise ValueError(f"Invalid distance_metric. Must be one of: {allowed}")
        return v


class EmbeddingConfig(BaseModel):
    """
    Configuration for embedding generation.

    Attributes:
        provider: Embedding provider (openai, sentence-transformers, etc.)
        model: Model name
        batch_size: Batch size for embedding generation
        cache_embeddings: Whether to cache embeddings
    """

    provider: str = Field(default="openai", description="Embedding provider")
    model: str = Field(default="text-embedding-ada-002", description="Model name")
    batch_size: int = Field(default=100, ge=1, description="Batch size")
    cache_embeddings: bool = Field(default=True, description="Cache embeddings")


class CompressionConfig(BaseModel):
    """
    Configuration for memory compression.

    Attributes:
        enabled: Enable automatic compression
        threshold_messages: Compress after this many messages
        threshold_age_days: Compress messages older than this
        summary_length: Target summary length
        keep_recent: Keep this many recent messages uncompressed
    """

    enabled: bool = Field(default=True, description="Enable compression")
    threshold_messages: int = Field(
        default=100, ge=1, description="Message count threshold"
    )
    threshold_age_days: int = Field(default=7, ge=1, description="Age threshold in days")
    summary_length: int = Field(default=500, ge=100, description="Summary length")
    keep_recent: int = Field(default=20, ge=1, description="Recent messages to keep")


def create_backend_config(backend_type: str, config_dict: Dict[str, Any]) -> BaseBackendConfig:
    """
    Create a backend configuration from a dictionary.

    Args:
        backend_type: Type of backend (sqlite, postgresql, redis, etc.)
        config_dict: Configuration parameters

    Returns:
        Validated configuration object

    Raises:
        ValueError: If backend_type is unknown or config is invalid

    Example:
        >>> config = create_backend_config("sqlite", {"database": "test.db"})
        >>> config.database
        'test.db'
    """
    config_classes = {
        "sqlite": SQLiteConfig,
        "postgresql": PostgreSQLConfig,
        "postgres": PostgreSQLConfig,
        "redis": RedisConfig,
        "chromadb": ChromaDBConfig,
        "chroma": ChromaDBConfig,
        "qdrant": QdrantConfig,
    }

    backend_type_lower = backend_type.lower()
    if backend_type_lower not in config_classes:
        raise ValueError(
            f"Unknown backend type: {backend_type}. "
            f"Available: {list(config_classes.keys())}"
        )

    config_class = config_classes[backend_type_lower]
    return config_class(**config_dict)
