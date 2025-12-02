"""
CurrentDate Tool - Returns current date and time information
"""

from datetime import datetime
from typing import Any, Dict
from app.mcp.base_tool import BaseTool
from app.core.utils import get_logger

logger = get_logger(__name__)


class CurrentDate(BaseTool):
    """Tool to get current date and time information"""

    async def execute(self, format: str = "full") -> Dict[str, Any]:
        """
        Get current date and time
        
        Args:
            format: Format type - 'full', 'date_only', 'time_only', 'iso'
            
        Returns:
            Dictionary with date/time information
        """
        now = datetime.utcnow()
        
        result = {
            "timestamp": now.isoformat(),
            "unix_timestamp": int(now.timestamp()),
        }
        
        if format in ["full", "date_only"]:
            result["date"] = now.strftime("%Y-%m-%d")
            result["date_readable"] = now.strftime("%A, %B %d, %Y")
        
        if format in ["full", "time_only"]:
            result["time"] = now.strftime("%H:%M:%S")
            result["time_with_tz"] = now.strftime("%H:%M:%S UTC")
        
        logger.info(f"CurrentDate tool executed with format: {format}")
        return result

    def get_schema(self) -> Dict[str, Any]:
        """Get input schema for CurrentDate tool"""
        return {
            "type": "object",
            "properties": {
                "format": {
                    "type": "string",
                    "enum": ["full", "date_only", "time_only", "iso"],
                    "description": "Format of the date/time output"
                }
            },
            "required": []
        }
