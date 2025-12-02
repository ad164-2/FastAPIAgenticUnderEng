"""
Base Tool Class - All MCP tools inherit from this
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from app.core.utils import get_logger

logger = get_logger(__name__)


class BaseTool(ABC):
    """Abstract base class for MCP tools"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the tool
        
        Args:
            config: Tool-specific configuration dictionary
        """
        self.config = config
        self.name = self.__class__.__name__
        logger.debug(f"Tool '{self.name}' initialized with config: {config}")

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        Execute the tool
        
        Args:
            **kwargs: Tool-specific arguments
            
        Returns:
            Tool result/output
        """
        pass

    def get_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for tool inputs
        Override this method to provide input schema
        
        Returns:
            JSON schema dictionary
        """
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
