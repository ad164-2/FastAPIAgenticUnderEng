"""
MCP Service - Exposes MCP tools through a service interface
"""

from typing import List, Dict, Any, Optional
from app.mcp.tool_manager import ToolManager, ToolInfo, ToolResult
from app.core.utils import get_logger

logger = get_logger(__name__)


class MCPService:
    """Service for managing and executing MCP tools"""

    _instance: Optional['MCPService'] = None

    def __new__(cls):
        """Singleton pattern for MCPService"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize MCP service"""
        if self._initialized:
            return
        
        self.tool_manager = ToolManager()
        self._initialized = True
        logger.info("MCP Service initialized")

    async def initialize(self) -> None:
        """Initialize all tools"""
        await self.tool_manager.initialize()
        logger.info("MCP Service tools loaded")

    def get_available_tools(self) -> List[ToolInfo]:
        """Get list of available tools"""
        return self.tool_manager.get_available_tools()

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool"""
        description = self.tool_manager.get_tool_description(tool_name)
        if not description:
            return None
        
        return {
            "name": tool_name,
            "description": description,
            "schema": self.tool_manager._get_tool_schema(tool_name)
        }

    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool arguments
            
        Returns:
            Tool execution result
        """
        result = await self.tool_manager.execute_tool(tool_name, **kwargs)
        return result.model_dump()

    def reload_configuration(self) -> None:
        """Reload MCP configuration"""
        self.tool_manager.reload_config()
        logger.info("MCP configuration reloaded")
