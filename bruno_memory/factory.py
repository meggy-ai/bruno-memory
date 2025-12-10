"""
Memory backend factory for creating and managing different storage backends.

Provides a centralized way to create backend instances based on configuration.
"""

import os
from typing import Dict, Type, Optional, Any, Union
from bruno_core.interfaces.memory_interface import MemoryInterface

from .base.memory_config import MemoryConfig, CONFIG_CLASSES
from .exceptions import BackendNotFoundError, ConfigurationError
from .backends.sqlite import SQLiteMemoryBackend


class MemoryFactory:
    """Factory class for creating memory backends."""
    
    _backends: Dict[str, Type[MemoryInterface]] = {}
    
    # Register built-in backends
    @classmethod
    def _register_builtin_backends(cls):
        """Register built-in backend implementations."""
        cls._backends["sqlite"] = SQLiteMemoryBackend
    
    @classmethod
    def _ensure_backends_registered(cls):
        """Ensure built-in backends are registered."""
        if not cls._backends:
            cls._register_builtin_backends()
    
    @classmethod
    def register_backend(cls, name: str, backend_class: Type[MemoryInterface]) -> None:
        """Register a backend implementation.
        
        Args:
            name: Backend name (e.g., 'sqlite', 'postgresql')
            backend_class: Backend implementation class
        """
        cls._backends[name] = backend_class
    
    @classmethod
    def get_backend_names(cls) -> list[str]:
        """Get list of registered backend names."""
        cls._ensure_backends_registered()
        return list(cls._backends.keys())
    
    @classmethod
    def create_backend(
        cls, 
        backend_type: str, 
        config: Optional[Union[Dict[str, Any], MemoryConfig]] = None,
        **kwargs
    ) -> MemoryInterface:
        """Create a backend instance.
        
        Args:
            backend_type: Type of backend to create
            config: Configuration dict or MemoryConfig instance
            **kwargs: Additional configuration parameters
            
        Returns:
            MemoryInterface implementation
            
        Raises:
            BackendNotFoundError: If backend type is not registered
            ConfigurationError: If configuration is invalid
        """
        cls._ensure_backends_registered()
        
        if backend_type not in cls._backends:
            raise BackendNotFoundError(
                f"Backend '{backend_type}' not found. "
                f"Available backends: {', '.join(cls.get_backend_names())}"
            )
        
        backend_class = cls._backends[backend_type]
        
        # Handle configuration
        if config is None:
            config = {}
        elif isinstance(config, MemoryConfig):
            config = config.dict()
        elif not isinstance(config, dict):
            raise ConfigurationError(
                f"Config must be dict or MemoryConfig instance, got {type(config)}"
            )
        
        # Merge kwargs into config
        config.update(kwargs)
        
        # Create config object
        config_class = CONFIG_CLASSES.get(backend_type)
        if config_class:
            try:
                validated_config = config_class(**config)
            except Exception as e:
                raise ConfigurationError(f"Invalid configuration for {backend_type}: {e}")
        else:
            validated_config = config
        
        # Create backend instance
        try:
            return backend_class(validated_config)
        except Exception as e:
            raise ConfigurationError(f"Failed to create {backend_type} backend: {e}")
    
    @classmethod
    def create_from_env(cls, prefix: str = "BRUNO_MEMORY") -> MemoryInterface:
        """Create backend from environment variables.
        
        Args:
            prefix: Environment variable prefix
            
        Returns:
            MemoryInterface implementation
            
        Example environment variables:
            BRUNO_MEMORY_BACKEND=sqlite
            BRUNO_MEMORY_DATABASE_PATH=./memory.db
        """
        backend_type = os.getenv(f"{prefix}_BACKEND")
        if not backend_type:
            raise ConfigurationError(f"Environment variable {prefix}_BACKEND not set")
        
        # Collect all environment variables with the prefix
        config = {}
        env_prefix = f"{prefix}_"
        
        for key, value in os.environ.items():
            if key.startswith(env_prefix) and key != f"{prefix}_BACKEND":
                # Convert BRUNO_MEMORY_DATABASE_PATH to database_path
                config_key = key[len(env_prefix):].lower()
                config[config_key] = value
        
        return cls.create_backend(backend_type, config)
    
    @classmethod
    def create_sqlite(
        cls, 
        database_path: str = "./memory.db",
        **kwargs
    ) -> MemoryInterface:
        """Convenience method to create SQLite backend.
        
        Args:
            database_path: Path to SQLite database file
            **kwargs: Additional configuration parameters
            
        Returns:
            SQLite MemoryInterface implementation
        """
        config = {"database_path": database_path, **kwargs}
        return cls.create_backend("sqlite", config)
    
    @classmethod
    def create_postgresql(
        cls,
        host: str = "localhost", 
        port: int = 5432,
        database: str = "bruno_memory",
        username: str = "postgres",
        password: str = "",
        **kwargs
    ) -> MemoryInterface:
        """Convenience method to create PostgreSQL backend.
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            username: Database username
            password: Database password
            **kwargs: Additional configuration parameters
            
        Returns:
            PostgreSQL MemoryInterface implementation
        """
        config = {
            "host": host,
            "port": port, 
            "database": database,
            "username": username,
            "password": password,
            **kwargs
        }
        return cls.create_backend("postgresql", config)
    
    @classmethod
    def create_redis(
        cls,
        host: str = "localhost",
        port: int = 6379, 
        password: Optional[str] = None,
        database: int = 0,
        **kwargs
    ) -> MemoryInterface:
        """Convenience method to create Redis backend.
        
        Args:
            host: Redis host
            port: Redis port
            password: Redis password
            database: Redis database number
            **kwargs: Additional configuration parameters
            
        Returns:
            Redis MemoryInterface implementation
        """
        config = {
            "host": host,
            "port": port,
            "database": database,
            **kwargs
        }
        if password:
            config["password"] = password
            
        return cls.create_backend("redis", config)