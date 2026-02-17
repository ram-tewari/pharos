"""Lazy import utilities for performance optimization.

This module provides mechanisms to defer expensive imports until they are actually needed,
significantly reducing CLI startup time.
"""

import importlib
from typing import Any, Callable, Optional, TypeVar, Generic, Dict


T = TypeVar('T')


class LazyLoader:
    """Lazy loader that imports a module or object on first access.
    
    Example:
        client = LazyLoader("pharos_cli.client.api_client", "APIClient")
        # No import happens here
        api_client = client.load()  # Import happens here
    """
    
    def __init__(
        self,
        module_name: str,
        object_name: Optional[str] = None,
        package: Optional[str] = None
    ):
        """Initialize lazy loader.
        
        Args:
            module_name: Full module path (e.g., "pharos_cli.client.api_client")
            object_name: Object name to import from module (None for module import)
            package: Package prefix for relative imports
        """
        self.module_name = module_name
        self.object_name = object_name
        self.package = package
        self._cached: Any = None
        self._loaded: bool = False
    
    def load(self) -> Any:
        """Load and return the requested object."""
        if self._loaded:
            return self._cached
        
        module = importlib.import_module(self.module_name)
        
        if self.object_name is None:
            self._cached = module
        else:
            self._cached = getattr(module, self.object_name)
        
        self._loaded = True
        return self._cached
    
    def __getattr__(self, name: str) -> Any:
        """Proxy attribute access to the loaded object."""
        obj = self.load()
        return getattr(obj, name)
    
    def __call__(self, *args, **kwargs) -> Any:
        """Call the loaded object as a function."""
        obj = self.load()
        return obj(*args, **kwargs)


class LazyModule:
    """A module-like object that defers imports until first use.
    
    Example:
        my_module = LazyModule("pharos_cli.commands.resource")
        my_module.resource_app  # Import happens here
    """
    
    def __init__(self, module_name: str, package: Optional[str] = None):
        self.module_name = module_name
        self.package = package
        self._module: Optional[Any] = None
    
    def __getattr__(self, name: str) -> Any:
        if self._module is None:
            self._module = importlib.import_module(self.module_name)
        return getattr(self._module, name)
    
    def __dir__(self):
        if self._module is None:
            self._module = importlib.import_module(self.module_name)
        return dir(self._module)


# Pre-defined lazy loaders for common expensive imports
LAZY_IMPORTS: Dict[str, Callable] = {
    # HTTP client
    'httpx': lambda: importlib.import_module('httpx'),
    'httpx_client': lambda: importlib.import_module('httpx').Client,
    'httpx_async_client': lambda: importlib.import_module('httpx').AsyncClient,
    
    # Authentication
    'keyring': lambda: importlib.import_module('keyring'),
    'keyring_backend': lambda: importlib.import_module('keyring.backends'),
    
    # Data validation
    'pydantic': lambda: importlib.import_module('pydantic'),
    'pydantic_base_model': lambda: importlib.import_module('pydantic').BaseModel,
    'pydantic_field': lambda: importlib.import_module('pydantic').Field,
    
    # YAML parsing
    'yaml': lambda: importlib.import_module('yaml'),
    'yaml_safe_load': lambda: importlib.import_module('yaml').safe_load,
    'yaml_dump': lambda: importlib.import_module('yaml').dump,
    
    # Rich (console output)
    'rich_print': lambda: importlib.import_module('rich').print,
    'rich_console': lambda: importlib.import_module('rich.console').Console,
    'rich_table': lambda: importlib.import_module('rich.table').Table,
    'rich_tree': lambda: importlib.import_module('rich.tree').Tree,
    'rich_panel': lambda: importlib.import_module('rich.panel').Panel,
    'rich_progress': lambda: importlib.import_module('rich.progress').Progress,
    'rich_live': lambda: importlib.import_module('rich.live').Live,
    'rich_spinner': lambda: importlib.import_module('rich.spinner').Spinner,
    
    # Typer (CLI framework)
    'typer': lambda: importlib.import_module('typer'),
    'typer_typer': lambda: importlib.import_module('typer').Typer,
    'typer_option': lambda: importlib.import_module('typer').Option,
    'typer_argument': lambda: importlib.import_module('typer').Argument,
    
    # Other utilities
    'dotenv': lambda: importlib.import_module('dotenv'),
    'tabulate': lambda: importlib.import_module('tabulate'),
    'tqdm': lambda: importlib.import_module('tqdm'),
}


def lazy_import(name: str) -> Callable[[], Any]:
    """Get a lazy import function for a named import.
    
    Args:
        name: Name of the import (e.g., 'httpx', 'rich')
    
    Returns:
        A callable that performs the import when called.
    
    Example:
        get_httpx = lazy_import('httpx')
        httpx = get_httpx()  # Import happens here
    """
    if name in LAZY_IMPORTS:
        return LAZY_IMPORTS[name]
    
    # Generic fallback
    def generic_import():
        return importlib.import_module(name)
    
    return generic_import


# Cache for loaded modules
_module_cache: Dict[str, Any] = {}


def cached_import(name: str) -> Any:
    """Import a module and cache the result.
    
    Args:
        name: Full module name.
    
    Returns:
        The imported module.
    """
    if name not in _module_cache:
        _module_cache[name] = importlib.import_module(name)
    return _module_cache[name]


def clear_import_cache() -> None:
    """Clear the import cache. Useful for testing."""
    _module_cache.clear()