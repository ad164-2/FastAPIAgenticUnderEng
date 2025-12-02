"""
Chat schemas for request/response validation
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request schema for chat endpoint"""
    query: str = Field(..., min_length=1, max_length=5000, description="User query for the agent")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the status of the deployment?"
            }
        }


class ChatResponse(BaseModel):
    """Response schema for chat endpoint"""
    query: str = Field(..., description="Original user query")
    response: str = Field(..., description="Agent response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the status of the deployment?",
                "response": "The deployment is currently in progress and should be completed within 5 minutes."
            }
        }
