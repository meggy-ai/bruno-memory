"""
Memory backend factory for creating and managing backend instances.

Provides a centralized factory pattern for creating memory backends
with proper configuration validation and type safety.
"""

from typing import Dict, Type, Any, Optional
import inspect

from .base import BaseMemoryBackend, MemoryConfig, CONFIG_CLASSES
from .exceptions import ConfigurationError, BackendNotFoundError, ValidationError


class MemoryBackendFactory:
    """Factory for creating memory backend instances."""
    
    def __init__(self):
        """Initialize the factory with empty backend registry."""
        self._backends: Dict[str, Type[BaseMemoryBackend]] = {}
        self._config_types: Dict[str, Type[MemoryConfig]] = CONFIG_CLASSES.copy()
    
    def register_backend(
        self,
        name: str,
        backend_class: Type[BaseMemoryBackend],
        config_class: Optional[Type[MemoryConfig]] = None
    ) -> None:
        """Register a memory backend implementation.
        
        Args:
            name: Backend name (e.g., 'sqlite', 'postgresql')
            backend_class: Backend implementation class
            config_class: Optional configuration class override
            
        Raises:
            ValidationError: If backend class is invalid
        """
        if not inspect.isclass(backend_class):
            raise ValidationError(f"Backend must be a class, got {type(backend_class)}")
        
        if not issubclass(backend_class, BaseMemoryBackend):
            raise ValidationError(
                f"Backend class must inherit from BaseMemoryBackend, "
                f"got {backend_class.__name__}"
            )
        
        self._backends[name] = backend_class
        
        if config_class:
            if not issubclass(config_class, MemoryConfig):
                raise ValidationError(
                    f"Config class must inherit from MemoryConfig, "
                    f"got {config_class.__name__}"
                )
            self._config_types[name] = config_class
    
    def unregister_backend(self, name: str) -> None:
        """Unregister a memory backend implementation.
        
        Args:
            name: Backend name to unregister
        """
        self._backends.pop(name, None)
        self._config_types.pop(name, None)
    
    def list_backends(self) -> Dict[str, str]:
        """List all registered backend implementations.
        
        Returns:
            Dictionary mapping backend names to class names
        """
        return {name: cls.__name__ for name, cls in self._backends.items()}
    
    def create_config(self, backend_type: str, **kwargs) -> MemoryConfig:
        """Create a configuration instance for the specified backend type.
        
        Args:
            backend_type: Backend type name
            **kwargs: Configuration parameters
            
        Returns:
            Configuration instance for the backend
            
        Raises:
            BackendNotFoundError: If backend type is not registered
            ConfigurationError: If configuration creation fails
        """
        if backend_type not in self._config_types:
            available = list(self._config_types.keys())
            raise BackendNotFoundError(
                f"Backend type '{backend_type}' not found. "
                f"Available backends: {available}"
            )
        
        config_class = self._config_types[backend_type]
        
        try:
            return config_class(**kwargs)
        except Exception as e:
            raise ConfigurationError(
                f"Failed to create {backend_type} configuration: {e}"
            )
    
    def create_backend(
        self,
        backend_type: str,
        config: Optional[MemoryConfig] = None,
        **config_kwargs
    ) -> BaseMemoryBackend:
        """Create a memory backend instance.
        
        Args:
            backend_type: Backend type name (e.g., 'sqlite', 'postgresql')
            config: Optional pre-created configuration instance
            **config_kwargs: Configuration parameters (if config not provided)
            
        Returns:
            Configured backend instance
            
        Raises:
            BackendNotFoundError: If backend type is not registered
            ConfigurationError: If configuration is invalid
        """
        if backend_type not in self._backends:
            available = list(self._backends.keys())
            raise BackendNotFoundError(
                f"Backend type '{backend_type}' not found. "
                f"Available backends: {available}"
            )
        
        # Create or validate configuration
        if config is None:
            config = self.create_config(backend_type, **config_kwargs)
        else:
            expected_type = self._config_types.get(backend_type)
            if expected_type and not isinstance(config, expected_type):
                raise ConfigurationError(
                    f"Invalid config type for {backend_type}. "
                    f"Expected {expected_type.__name__}, got {type(config).__name__}"
                )
        
        backend_class = self._backends[backend_type]
        
        try:
            return backend_class(config)
        except Exception as e:
            raise ConfigurationError(
                f"Failed to create {backend_type} backend: {e}"
            )
    
    def get_backend_class(self, backend_type: str) -> Type[BaseMemoryBackend]:
        """Get the backend class for a given type.
        
        Args:
            backend_type: Backend type name
            
        Returns:
            Backend class
            
        Raises:
            BackendNotFoundError: If backend type is not registered
        """
        if backend_type not in self._backends:
            available = list(self._backends.keys())
            raise BackendNotFoundError(
                f"Backend type '{backend_type}' not found. "
                f"Available backends: {available}"
            )
        
        return self._backends[backend_type]
    
    def get_config_class(self, backend_type: str) -> Type[MemoryConfig]:
        """Get the configuration class for a given backend type.
        
        Args:
            backend_type: Backend type name
            
        Returns:
            Configuration class
            
        Raises:
            BackendNotFoundError: If backend type is not registered
        """
        if backend_type not in self._config_types:
            available = list(self._config_types.keys())
            raise BackendNotFoundError(
                f"Backend type '{backend_type}' not found. "
                f"Available backends: {available}"
            )
        
        return self._config_types[backend_type]


# Global factory instance
factory = MemoryBackendFactory()

# Convenience functions that use the global factory
def register_backend(
    name: str,
    backend_class: Type[BaseMemoryBackend],
    config_class: Optional[Type[MemoryConfig]] = None
) -> None:
    """Register a memory backend implementation in the global factory.
    
    Args:
        name: Backend name
        backend_class: Backend implementation class
        config_class: Optional configuration class override
    """
    factory.register_backend(name, backend_class, config_class)


def create_backend(
    backend_type: str,
    config: Optional[MemoryConfig] = None,
    **config_kwargs
) -> BaseMemoryBackend:
    """Create a memory backend instance using the global factory.
    
    Args:
        backend_type: Backend type name
        config: Optional pre-created configuration instance
        **config_kwargs: Configuration parameters
        
    Returns:
        Configured backend instance
    """
    return factory.create_backend(backend_type, config, **config_kwargs)


def create_config(backend_type: str, **kwargs) -> MemoryConfig:
    """Create a configuration instance using the global factory.
    
    Args:
        backend_type: Backend type name
        **kwargs: Configuration parameters
        
    Returns:
        Configuration instance
    """
    return factory.create_config(backend_type, **kwargs)


def list_backends() -> Dict[str, str]:
    """List all registered backend implementations.
    
    Returns:
        Dictionary mapping backend names to class names
    """
    return factory.list_backends()


__all__ = [
    'MemoryBackendFactory',
    'factory',
    'register_backend',
    'create_backend',
    'create_config',
    'list_backends'
]