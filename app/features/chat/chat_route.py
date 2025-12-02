"""
Chat API endpoints - Agent-based chat interface for testing
"""

from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from app.features.chat.chat_schemas import ChatRequest, ChatResponse
from app.llm_functions.LLMCall import CallAgentGraph
from app.core.utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/invoke", response_model=ChatResponse)
async def invoke_agent(request: ChatRequest):
    """
    Invoke the agent graph with a user query.
    
    This endpoint sends a query through the agent graph which includes:
    1. Guardrail Agent - Validates the input
    2. Synthesize Response Agent - Generates the response
    
    Args:
        request: ChatRequest containing the user query
        
    Returns:
        ChatResponse with original query and agent response
    """
    try:
        logger.info(f"Chat invoke request: {request.query}")
        
        # Call the agent graph
        response = await CallAgentGraph(request.query)
        
        logger.info(f"Chat response generated: {response}")
        
        return ChatResponse(
            query=request.query,
            response=response
        )
        
    except Exception as e:
        logger.error(f"Error invoking agent: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/health")
def health_check():
    """Health check endpoint for the chat service"""
    logger.info("Chat service health check")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ok", "service": "chat"}
    )
