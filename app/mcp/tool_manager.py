"""
Tool Manager - Orchestrates MCP tool loading and execution
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.core.utils import get_logger
from app.mcp.tool_registry import ToolRegistry
from app.mcp.tool_loader import ToolLoader

logger = get_logger(__name__)


class ToolInfo(BaseModel):
    """Information about an available tool"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    enabled: bool = Field(..., description="Whether tool is enabled")
    input_schema: Dict[str, Any] = Field(default_factory=dict, description="Tool input schema")


class ToolResult(BaseModel):
    """Result from tool execution"""
    success: bool = Field(..., description="Whether execution succeeded")
    data: Any = Field(..., description="Tool output data")
    error: Optional[str] = Field(None, description="Error message if execution failed")


class ToolManager:
    """
    Orchestrates MCP tool discovery, loading, and execution
    Acts as the central hub for agent-tool interactions
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the tool manager
        
        Args:
            config_path: Path to mcp_config.json
        """
        self.registry = ToolRegistry(config_path)
        self.loader = ToolLoader(self.registry)
        self._tools: Optional[Dict[str, Any]] = None
        logger.info("Tool manager initialized")

    async def initialize(self) -> None:
        """Initialize and load all enabled tools"""
        self._tools = self.loader.load_all_tools()
        logger.info(f"Tool manager initialized with {len(self._tools)} tools")

    def get_available_tools(self) -> List[ToolInfo]:
        """
        Get information about all available tools
        
        Returns:
            List of ToolInfo objects
        """
        tools_info = []
        for tool_name, config in self.registry.get_enabled_tools().items():
            tool_info = ToolInfo(
                name=tool_name,
                description=config.description,
                enabled=True,
                input_schema=self._get_tool_schema(tool_name)
            )
            tools_info.append(tool_info)
        
        return tools_info

    def get_tool_description(self, tool_name: str) -> Optional[str]:
        """Get description for a specific tool"""
        return self.registry.get_tool_description(tool_name)

    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """
        Execute a tool
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Arguments to pass to the tool
            
        Returns:
            ToolResult with execution result
        """
        try:
            if self._tools is None:
                await self.initialize()

            if tool_name not in self._tools:
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Tool '{tool_name}' not found or not enabled"
                )

            tool = self._tools[tool_name]
            
            logger.info(f"Executing tool '{tool_name}' with args: {kwargs}")
            
            # Call the tool's execute method
            result = await tool.execute(**kwargs)
            
            logger.info(f"Tool '{tool_name}' executed successfully")
            
            return ToolResult(
                success=True,
                data=result,
                error=None
            )

        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {str(e)}", exc_info=True)
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )

    def _get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """
        Get JSON schema for tool inputs
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            JSON schema for the tool
        """
        if self._tools is None or tool_name not in self._tools:
            return {}
        
        tool = self._tools[tool_name]
        
        # Check if tool has a schema method
        if hasattr(tool, 'get_schema'):
            return tool.get_schema()
        
        return {}

    def reload_config(self) -> None:
        """Reload configuration and clear tool cache"""
        self.registry.reload_config()
        self.loader.clear_cache()
        self._tools = None
        logger.info("Tool manager configuration reloaded")
