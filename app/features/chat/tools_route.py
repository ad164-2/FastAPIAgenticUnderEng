"""
MCP API endpoints - Expose MCP tools through REST API for testing
"""

from fastapi import APIRouter, status, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from app.mcp.mcp_service import MCPService
from app.core.utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/tools", tags=["tools"])

# Initialize MCP service
mcp_service = MCPService()


class ToolExecuteRequest(BaseModel):
    """Request to execute a tool"""
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")


class ToolInfo(BaseModel):
    """Information about an available tool"""
    name: str
    description: str
    schema: Dict[str, Any]


@router.get("/list", response_model=Dict[str, Any])
async def list_tools():
    """
    List all available MCP tools
    
    Returns:
        List of available tools with descriptions
    """
    try:
        logger.info("Listing available tools")
        tools = mcp_service.get_available_tools()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "count": len(tools),
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "enabled": tool.enabled,
                        "schema": tool.input_schema
                    }
                    for tool in tools
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error listing tools: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing tools: {str(e)}"
        )


@router.get("/{tool_name}")
async def get_tool(tool_name: str):
    """
    Get information about a specific tool
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Tool information including schema
    """
    try:
        logger.info(f"Getting tool info: {tool_name}")
        tool_info = mcp_service.get_tool_info(tool_name)
        
        if not tool_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool '{tool_name}' not found or not enabled"
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "tool": tool_info
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tool '{tool_name}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting tool info: {str(e)}"
        )


@router.post("/{tool_name}/execute")
async def execute_tool(tool_name: str, request: ToolExecuteRequest):
    """
    Execute a specific tool
    
    Args:
        tool_name: Name of the tool to execute
        request: Tool execution request with parameters
        
    Returns:
        Tool execution result
    """
    try:
        logger.info(f"Executing tool: {tool_name} with params: {request.parameters}")
        
        result = await mcp_service.execute_tool(tool_name, **request.parameters)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": result["success"],
                "tool": tool_name,
                "data": result["data"],
                "error": result["error"]
            }
        )
    except Exception as e:
        logger.error(f"Error executing tool '{tool_name}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing tool: {str(e)}"
        )


@router.post("/reload-config")
async def reload_config():
    """
    Reload MCP configuration from file
    
    Returns:
        Success status
    """
    try:
        logger.info("Reloading MCP configuration")
        mcp_service.reload_configuration()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "MCP configuration reloaded successfully"
            }
        )
    except Exception as e:
        logger.error(f"Error reloading configuration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reloading configuration: {str(e)}"
        )
