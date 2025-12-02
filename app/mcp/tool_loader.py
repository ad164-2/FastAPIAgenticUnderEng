"""
Tool Loader - Dynamically loads and instantiates MCP tools
"""

from typing import Any, Dict, Optional
from app.core.utils import get_logger
from app.mcp.tool_registry import ToolRegistry

logger = get_logger(__name__)


class ToolLoader:
    """Dynamically loads MCP tools based on registry configuration"""

    # Mapping of tool names to their implementation modules
    TOOL_IMPLEMENTATIONS = {
        "google_search": "app.mcp.tools.google_search",
        "sqlite": "app.mcp.tools.sqlite_tool",
        "current_date": "app.mcp.tools.current_date",
    }

    def __init__(self, registry: ToolRegistry):
        """
        Initialize the tool loader
        
        Args:
            registry: ToolRegistry instance
        """
        self.registry = registry
        self._tool_cache: Dict[str, Any] = {}
        logger.info("Tool loader initialized")

    async def load_tool(self, tool_name: str) -> Optional[Any]:
        """
        Dynamically load a tool
        
        Args:
            tool_name: Name of the tool to load
            
        Returns:
            Tool instance or None if not found/enabled
        """
        # Check if tool is already cached
        if tool_name in self._tool_cache:
            logger.debug(f"Tool '{tool_name}' loaded from cache")
            return self._tool_cache[tool_name]

        # Check if tool is enabled
        if not self.registry.is_tool_enabled(tool_name):
            logger.warning(f"Tool '{tool_name}' is not enabled")
            return None

        try:
            tool_config = self.registry.get_tool_config(tool_name)
            if not tool_config:
                logger.error(f"Tool '{tool_name}' not found in registry")
                return None

            # Interpolate environment variables in config
            config = self.registry.interpolate_config(tool_config.config)

            # Get the implementation module path
            module_path = self.TOOL_IMPLEMENTATIONS.get(tool_name)
            if not module_path:
                logger.error(f"No implementation found for tool '{tool_name}'")
                return None

            # Dynamically import the tool module
            module = self._import_module(module_path)
            
            # Get the tool class (convention: class name is PascalCase of tool_name)
            class_name = self._to_pascal_case(tool_name)
            if not hasattr(module, class_name):
                logger.error(f"Tool class '{class_name}' not found in {module_path}")
                return None

            tool_class = getattr(module, class_name)
            
            # Instantiate the tool
            tool_instance = tool_class(config)
            logger.info(f"Tool '{tool_name}' loaded successfully")
            
            # Cache the tool
            self._tool_cache[tool_name] = tool_instance
            
            return tool_instance

        except Exception as e:
            logger.error(f"Failed to load tool '{tool_name}': {str(e)}", exc_info=True)
            return None

    def load_all_tools(self) -> Dict[str, Any]:
        """
        Load all enabled tools
        
        Returns:
            Dictionary of loaded tools
        """
        tools = {}
        enabled_tools = self.registry.get_enabled_tools()
        
        for tool_name in enabled_tools.keys():
            tool = self.load_tool(tool_name)
            if tool:
                tools[tool_name] = tool
        
        logger.info(f"Loaded {len(tools)} tools")
        return tools

    @staticmethod
    def _import_module(module_path: str) -> Any:
        """
        Dynamically import a module
        
        Args:
            module_path: Fully qualified module path (e.g., 'app.mcp.tools.google_search')
            
        Returns:
            Imported module
        """
        import importlib
        return importlib.import_module(module_path)

    @staticmethod
    def _to_pascal_case(snake_str: str) -> str:
        """Convert snake_case to PascalCase"""
        return ''.join(word.capitalize() for word in snake_str.split('_'))

    def clear_cache(self) -> None:
        """Clear the tool cache"""
        self._tool_cache.clear()
        logger.info("Tool cache cleared")
