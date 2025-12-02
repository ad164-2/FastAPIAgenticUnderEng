"""
Tool Registry - Manages MCP tool configuration and discovery
"""

import json
import os
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from app.core.utils import get_logger

logger = get_logger(__name__)


class ToolConfig(BaseModel):
    """Configuration for a single MCP tool"""
    enabled: bool = Field(..., description="Whether the tool is enabled")
    description: str = Field(..., description="Tool description")
    config: Dict[str, Any] = Field(default_factory=dict, description="Tool-specific configuration")


class MCPConfig(BaseModel):
    """Root MCP configuration"""
    version: str = Field(default="1.0", description="Configuration version")
    tools: Dict[str, ToolConfig] = Field(default_factory=dict, description="Available tools")


class ToolRegistry:
    """Registry for managing MCP tool configurations"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the tool registry
        
        Args:
            config_path: Path to mcp_config.json. Defaults to app/mcp/mcp_config.json
        """
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "mcp_config.json")
        
        self.config_path = config_path
        self.config = self._load_config()
        logger.info(f"Tool registry initialized with config: {config_path}")

    def _load_config(self) -> MCPConfig:
        """Load and parse the MCP configuration"""
        try:
            if not os.path.exists(self.config_path):
                logger.warning(f"Config file not found: {self.config_path}. Using empty config.")
                return MCPConfig(tools={})
            
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
            
            config = MCPConfig(**config_data)
            logger.info(f"Loaded MCP configuration with {len(config.tools)} tools")
            return config
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse MCP config JSON: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to load MCP config: {str(e)}")
            raise

    def get_enabled_tools(self) -> Dict[str, ToolConfig]:
        """Get all enabled tools"""
        return {name: tool for name, tool in self.config.tools.items() if tool.enabled}

    def get_tool_config(self, tool_name: str) -> Optional[ToolConfig]:
        """Get configuration for a specific tool"""
        return self.config.tools.get(tool_name)

    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a tool is enabled"""
        tool = self.config.tools.get(tool_name)
        return tool.enabled if tool else False

    def get_tool_description(self, tool_name: str) -> Optional[str]:
        """Get description for a tool"""
        tool = self.config.tools.get(tool_name)
        return tool.description if tool else None

    def interpolate_config(self, tool_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interpolate environment variables in config values
        Supports ${VAR_NAME} syntax
        """
        result = {}
        for key, value in tool_config.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                result[key] = os.getenv(env_var, value)
            else:
                result[key] = value
        return result

    def reload_config(self) -> None:
        """Reload configuration from file"""
        self.config = self._load_config()
        logger.info("Tool registry configuration reloaded")
