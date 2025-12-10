"""Factory for creating memory backends."""

import os
from typing import Any, Dict, Optional, Type, List, Union
from importlib.metadata import entry_points

from bruno_memory.base import MemoryConfig, BaseMemoryBackend, create_config
from bruno_memory.exceptions import BackendNotAvailableError, ConfigurationError


class MemoryFactory:
    """Factory for creating memory backend instances."""
    
    _registered_backends: Dict[str, Type[BaseMemoryBackend]] = {}
    _backend_configs: Dict[str, Type[MemoryConfig]] = {}
    
    @classmethod
    def register(
        self,
        name: str,
        backend_class: Type[BaseMemoryBackend],
        config_class: Type[MemoryConfig],
    ) -> None:
        """Register a memory backend.
        
        Args:
            name: Backend name (e.g., 'sqlite', 'postgresql')
            backend_class: Backend implementation class
            config_class: Configuration class for the backend
        """
        self._registered_backends[name] = backend_class
        self._backend_configs[name] = config_class
    
    @classmethod
    def create(
        cls,
        backend_type: str,
        config: Optional[Union[Dict[str, Any], MemoryConfig]] = None,
        **kwargs
    ) -> BaseMemoryBackend:
        """Create a memory backend instance.
        
        Args:
            backend_type: Type of backend to create
            config: Configuration dict or MemoryConfig instance
            **kwargs: Additional config parameters
            
        Returns:
            Initialized backend instance
            
        Raises:
            BackendNotAvailableError: If backend is not available
            ConfigurationError: If configuration is invalid
        """
        # Ensure backends are discovered
        cls._discover_backends()
        
        # Check if backend is registered
        if backend_type not in cls._registered_backends:
            available = list(cls._registered_backends.keys())
            raise BackendNotAvailableError(
                backend_type,
                f"Available backends: {available}"
            )
        
        # Create configuration
        if isinstance(config, MemoryConfig):
            backend_config = config
        else:
            config_dict = config or {}
            config_dict.update(kwargs)
            backend_config = create_config(backend_type, config_dict)
        
        # Create backend instance
        backend_class = cls._registered_backends[backend_type]
        try:
            return backend_class(backend_config)
        except Exception as e:
            raise ConfigurationError(f"Failed to create {backend_type} backend: {e}") from e
    
    @classmethod
    def create_from_env(
        cls,
        backend_type: Optional[str] = None,
        prefix: str = "BRUNO_MEMORY_"
    ) -> BaseMemoryBackend:
        """Create backend from environment variables.
        
        Args:
            backend_type: Backend type (if None, read from env)
            prefix: Environment variable prefix
            
        Returns:
            Configured backend instance
        """
        # Get backend type from env if not provided
        if backend_type is None:
            backend_type = os.getenv(f"{prefix}BACKEND", "sqlite")
        
        # Build config from environment variables
        config_dict = {}
        
        # Common settings
        if timeout := os.getenv(f"{prefix}TIMEOUT"):
            config_dict["connection_timeout"] = int(timeout)
        
        if max_conn := os.getenv(f"{prefix}MAX_CONNECTIONS"):
            config_dict["max_connections"] = int(max_conn)
        
        # Backend-specific settings
        if backend_type == "sqlite":
            if db_path := os.getenv(f"{prefix}DATABASE_PATH"):
                config_dict["database_path"] = db_path
            if fts := os.getenv(f"{prefix}ENABLE_FTS"):
                config_dict["enable_fts"] = fts.lower() in ("true", "1", "yes")
                
        elif backend_type == "postgresql":
            if url := os.getenv(f"{prefix}DATABASE_URL"):
                # Parse database URL
                from urllib.parse import urlparse
                parsed = urlparse(url)
                config_dict.update({
                    "host": parsed.hostname,
                    "port": parsed.port or 5432,
                    "database": parsed.path.lstrip("/"),
                    "username": parsed.username,
                    "password": parsed.password,
                })
            else:
                if host := os.getenv(f"{prefix}HOST"):
                    config_dict["host"] = host
                if port := os.getenv(f"{prefix}PORT"):
                    config_dict["port"] = int(port)
                if database := os.getenv(f"{prefix}DATABASE"):
                    config_dict["database"] = database
                if username := os.getenv(f"{prefix}USERNAME"):
                    config_dict["username"] = username
                if password := os.getenv(f"{prefix}PASSWORD"):
                    config_dict["password"] = password
                    
        elif backend_type == "redis":
            if url := os.getenv(f"{prefix}REDIS_URL"):
                from urllib.parse import urlparse
                parsed = urlparse(url)
                config_dict.update({
                    "host": parsed.hostname,
                    "port": parsed.port or 6379,
                    "db": int(parsed.path.lstrip("/")) if parsed.path else 0,
                    "password": parsed.password,
                })
            else:
                if host := os.getenv(f"{prefix}REDIS_HOST"):
                    config_dict["host"] = host
                if port := os.getenv(f"{prefix}REDIS_PORT"):
                    config_dict["port"] = int(port)
                if db := os.getenv(f"{prefix}REDIS_DB"):
                    config_dict["db"] = int(db)
                if password := os.getenv(f"{prefix}REDIS_PASSWORD"):
                    config_dict["password"] = password
            
            if ttl := os.getenv(f"{prefix}TTL_SECONDS"):
                config_dict["ttl_seconds"] = int(ttl)
                
        elif backend_type in ("chromadb", "qdrant"):
            if persist_dir := os.getenv(f"{prefix}PERSIST_DIRECTORY"):
                config_dict["persist_directory"] = persist_dir
            if collection := os.getenv(f"{prefix}COLLECTION_NAME"):
                config_dict["collection_name"] = collection
        
        return cls.create(backend_type, config_dict)
    
    @classmethod
    def create_with_fallback(
        cls,
        backend_types: List[str],
        config: Optional[Dict[str, Any]] = None
    ) -> BaseMemoryBackend:
        """Create backend with fallback options.
        
        Tries backends in order until one succeeds.
        
        Args:
            backend_types: List of backend types to try in order
            config: Configuration to use for all backends
            
        Returns:
            First successfully created backend
            
        Raises:
            BackendNotAvailableError: If no backends can be created
        """
        errors = []
        
        for backend_type in backend_types:
            try:
                return cls.create(backend_type, config)
            except Exception as e:
                errors.append(f"{backend_type}: {e}")
                continue
        
        raise BackendNotAvailableError(
            ", ".join(backend_types),
            f"All backends failed: {'; '.join(errors)}"
        )
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """List available backend providers.
        
        Returns:
            List of registered backend names
        """
        cls._discover_backends()
        return list(cls._registered_backends.keys())
    
    @classmethod
    def is_registered(cls, backend_type: str) -> bool:
        """Check if backend type is registered.
        
        Args:
            backend_type: Backend type to check
            
        Returns:
            True if backend is registered
        """
        cls._discover_backends()
        return backend_type in cls._registered_backends
    
    @classmethod
    def _discover_backends(cls) -> None:
        """Discover and register backends from entry points."""
        if cls._registered_backends:
            return  # Already discovered
        
        # Register built-in backends
        cls._register_builtin_backends()
        
        # Discover entry points
        try:
            for entry_point in entry_points(group="bruno_memory.backends"):
                try:
                    backend_class = entry_point.load()
                    # Get config class (assume it's in the same module)
                    config_class = getattr(backend_class, "CONFIG_CLASS", None)
                    if config_class:
                        cls.register(entry_point.name, backend_class, config_class)
                except Exception:
                    # Skip failed entry points
                    continue
        except Exception:
            # Entry points not available or failed
            pass
    
    @classmethod
    def _register_builtin_backends(cls) -> None:
        """Register built-in backends."""
        # Import and register built-in backends
        
        # SQLite backend
        try:
            from bruno_memory.backends.sqlite import SQLiteBackend
            from bruno_memory.base.memory_config import SQLiteConfig
            cls.register("sqlite", SQLiteBackend, SQLiteConfig)
        except ImportError:
            pass
        
        # PostgreSQL backend
        try:
            from bruno_memory.backends.postgresql import PostgreSQLBackend
            from bruno_memory.base.memory_config import PostgreSQLConfig
            cls.register("postgresql", PostgreSQLBackend, PostgreSQLConfig)
        except ImportError:
            pass
        
        # Redis backend
        try:
            from bruno_memory.backends.redis import RedisBackend
            from bruno_memory.base.memory_config import RedisConfig
            cls.register("redis", RedisBackend, RedisConfig)
        except ImportError:
            pass
        
        # ChromaDB backend
        try:
            from bruno_memory.backends.vector import ChromaDBBackend
            from bruno_memory.base.memory_config import ChromaDBConfig
            cls.register("chromadb", ChromaDBBackend, ChromaDBConfig)
        except ImportError:
            pass
        
        # Qdrant backend
        try:
            from bruno_memory.backends.vector import QdrantBackend
            from bruno_memory.base.memory_config import QdrantConfig
            cls.register("qdrant", QdrantBackend, QdrantConfig)
        except ImportError:
            pass