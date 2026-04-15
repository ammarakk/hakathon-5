"""
MCP Server API Endpoints
"""

from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
import logging

from app.mcp.server import mcp_server
from app.mcp.agent_integration import enhanced_agent_service

logger = logging.getLogger(__name__)

router = APIRouter()


class ToolCallRequest(BaseModel):
    """Tool call request schema"""
    tool_name: str = Field(..., description="Name of the tool to call")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")


class ToolCallResponse(BaseModel):
    """Tool call response schema"""
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AgentWithToolsRequest(BaseModel):
    """Agent request with tool integration"""
    message: str = Field(..., min_length=1, description="Customer message")
    channel: str = Field("web", description="Communication channel")
    customer_context: Optional[Dict[str, Any]] = Field(None, description="Customer information")


@router.get("/tools", status_code=status.HTTP_200_OK)
async def list_tools():
    """
    List all available MCP tools

    Returns:
        List of tool definitions
    """
    try:
        tools = mcp_server.list_tools()

        return {
            "success": True,
            "count": len(tools),
            "tools": tools
        }

    except Exception as e:
        logger.error(f"❌ Error listing tools: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing tools: {str(e)}"
        )


@router.get("/tools/{tool_name}", status_code=status.HTTP_200_OK)
async def get_tool_info(tool_name: str):
    """
    Get information about a specific tool

    Args:
        tool_name: Name of the tool

    Returns:
        Tool definition
    """
    try:
        tool_info = mcp_server.get_tool_info(tool_name)

        if not tool_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool '{tool_name}' not found"
            )

        return {
            "success": True,
            "tool": tool_info
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting tool info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting tool info: {str(e)}"
        )


@router.post("/tools/call", status_code=status.HTTP_200_OK, response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest):
    """
    Call an MCP tool directly

    Args:
        request: Tool call request with tool name and parameters

    Returns:
        Tool execution result
    """
    try:
        result = await mcp_server.call_tool(
            tool_name=request.tool_name,
            parameters=request.parameters
        )

        if result.get("success"):
            return ToolCallResponse(
                success=True,
                result=result
            )
        else:
            return ToolCallResponse(
                success=False,
                error=result.get("error", "Tool execution failed")
            )

    except Exception as e:
        logger.error(f"❌ Error calling tool {request.tool_name}: {e}")
        return ToolCallResponse(
            success=False,
            error=str(e)
        )


@router.post("/agent/chat", status_code=status.HTTP_200_OK)
async def chat_with_enhanced_agent(request: AgentWithToolsRequest):
    """
    Chat with enhanced AI agent with MCP tool integration

    Args:
        request: Chat request with message and context

    Returns:
        Agent response with tool usage
    """
    try:
        result = await enhanced_agent_service.process_with_tools(
            message=request.message,
            channel=request.channel,
            customer_context=request.customer_context
        )

        return {
            "success": True,
            "response": result["response"],
            "tools_enabled": result["tools_enabled"]
        }

    except Exception as e:
        logger.error(f"❌ Error in enhanced agent chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat: {str(e)}"
        )


@router.get("/status", status_code=status.HTTP_200_OK)
async def get_mcp_status():
    """
    Get MCP server status

    Returns:
        MCP server information
    """
    tools = mcp_server.list_tools()

    return {
        "status": "operational",
        "server": "Nur Scents MCP Server",
        "version": "1.0.0",
        "tools_count": len(tools),
        "tools_available": [t["name"] for t in tools],
        "capabilities": [
            "product_search",
            "product_management",
            "customer_management",
            "order_management",
            "recommendations",
            "conversation_tracking"
        ]
    }
