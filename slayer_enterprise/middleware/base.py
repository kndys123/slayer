"""
Plugin and middleware system for extensibility.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
import importlib
import os
from pathlib import Path


class Middleware(ABC):
    """Base class for middleware."""
    
    @abstractmethod
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process request before execution."""
        pass
    
    @abstractmethod
    async def process_response(self, response: Any) -> Any:
        """Process response after execution."""
        pass


class Plugin(ABC):
    """Base class for plugins."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.enabled = True
    
    @abstractmethod
    def get_name(self) -> str:
        """Get plugin name."""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Get plugin version."""
        pass
    
    @abstractmethod
    async def initialize(self):
        """Initialize plugin."""
        pass
    
    @abstractmethod
    async def shutdown(self):
        """Shutdown plugin."""
        pass


class PluginManager:
    """Manages plugins and their lifecycle."""
    
    def __init__(self, plugin_dir: str = "./plugins"):
        self.plugin_dir = Path(plugin_dir)
        self._plugins: Dict[str, Plugin] = {}
        self._middlewares: List[Middleware] = []
    
    def register_plugin(self, plugin: Plugin):
        """Register a plugin."""
        name = plugin.get_name()
        self._plugins[name] = plugin
    
    def unregister_plugin(self, name: str):
        """Unregister a plugin."""
        if name in self._plugins:
            del self._plugins[name]
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get plugin by name."""
        return self._plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        """List all registered plugins."""
        return list(self._plugins.keys())
    
    async def initialize_all(self):
        """Initialize all plugins."""
        for plugin in self._plugins.values():
            if plugin.enabled:
                await plugin.initialize()
    
    async def shutdown_all(self):
        """Shutdown all plugins."""
        for plugin in self._plugins.values():
            await plugin.shutdown()
    
    def load_from_directory(self):
        """Auto-load plugins from directory."""
        if not self.plugin_dir.exists():
            return
        
        # This would implement dynamic plugin loading
        # For now, plugins need to be registered manually
        pass
