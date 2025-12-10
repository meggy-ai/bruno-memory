"""Configuration models for bruno-memory backends."""

from typing import Any, Dict, Optional, Union
from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel, Field, validator, ConfigDict


class MemoryConfig(BaseModel, ABC):
    """Base configuration for memory backends."""
    
    model_config = ConfigDict(extra='forbid', validate_assignment=True)
    
    # Common settings
    max_connections: int = Field(default=10, ge=1, le=100)
    connection_timeout: int = Field(default=30, ge=1, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)
    
    @abstractmethod
    def get_connection_string(self) -> str:
        """Get connection string for this backend."""
        pass


class SQLiteConfig(MemoryConfig):
    """Configuration for SQLite backend."""
    
    database_path: Union[str, Path] = Field(default="./bruno_memory.db")
    enable_wal: bool = Field(default=True, description="Enable Write-Ahead Logging")
    enable_fts: bool = Field(default=True, description="Enable Full-Text Search")
    pragma_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "journal_mode": "WAL",
            "synchronous": "NORMAL", 
            "cache_size": -64000,  # 64MB cache
            "foreign_keys": 1,
            "temp_store": "memory"
        }
    )
    
    @validator('database_path')
    def validate_database_path(cls, v):
        """Ensure database path is valid."""
        path = Path(v)
        # Create parent directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path.resolve())
    
    def get_connection_string(self) -> str:
        """Get SQLite connection string."""
        return f"sqlite:///{self.database_path}"


class PostgreSQLConfig(MemoryConfig):
    """Configuration for PostgreSQL backend."""
    
    host: str = Field(default="localhost")
    port: int = Field(default=5432, ge=1, le=65535)
    database: str = Field(default="bruno_memory")
    username: str = Field(default="postgres")
    password: str = Field(default="")
    db_schema: str = Field(default="public", alias="schema")
    
    # Connection pool settings
    pool_size: int = Field(default=20, ge=1, le=100)
    max_overflow: int = Field(default=10, ge=0, le=50)
    
    # SSL settings
    ssl_mode: str = Field(default="prefer")
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    ssl_ca_path: Optional[str] = None
    
    # Vector extension settings
    enable_pgvector: bool = Field(default=True)
    vector_dimensions: int = Field(default=1536, ge=1, le=4096)
    
    def get_connection_string(self) -> str:
        """Get PostgreSQL connection string."""
        auth = f"{self.username}:{self.password}" if self.password else self.username
        return f"postgresql://{auth}@{self.host}:{self.port}/{self.database}"


class RedisConfig(MemoryConfig):
    """Configuration for Redis backend."""
    
    host: str = Field(default="localhost")
    port: int = Field(default=6379, ge=1, le=65535)
    db: int = Field(default=0, ge=0, le=15)
    password: Optional[str] = None
    
    # Redis-specific settings
    ttl_seconds: int = Field(default=3600, ge=60, le=86400 * 7)  # 1 hour to 7 days
    max_memory_policy: str = Field(default="allkeys-lru")
    
    # Connection pool settings  
    decode_responses: bool = Field(default=True)
    socket_timeout: int = Field(default=5, ge=1, le=60)
    socket_connect_timeout: int = Field(default=5, ge=1, le=60)
    
    # Cluster settings
    cluster_mode: bool = Field(default=False)
    cluster_nodes: Optional[list[Dict[str, Union[str, int]]]] = None
    
    def get_connection_string(self) -> str:
        """Get Redis connection string."""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class ChromaDBConfig(MemoryConfig):
    """Configuration for ChromaDB backend."""
    
    persist_directory: Union[str, Path] = Field(default="./chroma_db")
    collection_name: str = Field(default="bruno_conversations")
    
    # Embedding settings
    embedding_function: Optional[str] = Field(default=None)
    distance_metric: str = Field(default="cosine")
    
    # Performance settings
    batch_size: int = Field(default=100, ge=1, le=1000)
    
    @validator('persist_directory')
    def validate_persist_directory(cls, v):
        """Ensure persist directory exists."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return str(path.resolve())
    
    def get_connection_string(self) -> str:
        """Get ChromaDB connection string."""
        return f"chromadb://{self.persist_directory}"


class QdrantConfig(MemoryConfig):
    """Configuration for Qdrant backend."""
    
    # Connection settings
    host: str = Field(default="localhost") 
    port: int = Field(default=6333, ge=1, le=65535)
    grpc_port: int = Field(default=6334, ge=1, le=65535)
    prefer_grpc: bool = Field(default=True)
    
    # Authentication
    api_key: Optional[str] = None
    
    # Collection settings
    collection_name: str = Field(default="bruno_conversations")
    vector_size: int = Field(default=1536, ge=1, le=4096)
    distance_metric: str = Field(default="Cosine")
    
    # Performance settings
    batch_size: int = Field(default=100, ge=1, le=1000)
    parallel: int = Field(default=1, ge=1, le=10)
    
    def get_connection_string(self) -> str:
        """Get Qdrant connection string."""
        protocol = "grpc" if self.prefer_grpc else "http"
        port = self.grpc_port if self.prefer_grpc else self.port
        return f"qdrant://{self.host}:{port}"


# Configuration factory
CONFIG_CLASSES = {
    "sqlite": SQLiteConfig,
    "postgresql": PostgreSQLConfig,
    "redis": RedisConfig, 
    "chromadb": ChromaDBConfig,
    "qdrant": QdrantConfig,
}


def create_config(backend_type: str, config_dict: Optional[Dict[str, Any]] = None) -> MemoryConfig:
    """Create configuration instance for backend type."""
    if backend_type not in CONFIG_CLASSES:
        available = ", ".join(CONFIG_CLASSES.keys())
        raise ValueError(f"Unknown backend type: {backend_type}. Available: {available}")
    
    config_class = CONFIG_CLASSES[backend_type]
    config_dict = config_dict or {}
    
    return config_class(**config_dict)