"""
Agent chat endpoint for testing and direct interaction
"""

from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.services.agent_service import agent_service
from app.services.customer_service import customer_service
from app.services.conversation_service import conversation_service
from pydantic import BaseModel, Field
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request schema"""
    message: str = Field(..., min_length=1, description="Customer message")
    channel: str = Field("web", description="Communication channel (whatsapp, email, web)")
    customer_phone: Optional[str] = Field(None, description="Customer phone number")
    customer_email: Optional[str] = Field(None, description="Customer email")
    customer_name: Optional[str] = Field(None, description="Customer name")


class ChatResponse(BaseModel):
    """Chat response schema"""
    success: bool = True
    response: str
    escalated: bool = False
    escalation_reason: Optional[str] = None


@router.post("/chat", status_code=status.HTTP_200_OK, response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Chat directly with the AI agent

    Args:
        request: Chat request with message and customer info
        db: Database session

    Returns:
        Agent response
    """
    try:
        # Get or create customer
        customer = None
        customer_context = {}

        if request.customer_phone:
            customer = await customer_service.get_customer_by_phone(
                db, request.customer_phone
            )

            if not customer and request.customer_name:
                customer = await customer_service.create_or_update_customer(
                    db=db,
                    phone_number=request.customer_phone,
                    name=request.customer_name,
                    email=request.customer_email,
                    preferred_channel=request.channel,
                )
        elif request.customer_email:
            customer = await customer_service.get_customer_by_email(
                db, request.customer_email
            )

        # Build customer context
        if customer:
            customer_context = customer.to_dict()

        # Process message with agent
        response = await agent_service.process_customer_message(
            message=request.message,
            channel=request.channel,
            customer_context=customer_context,
            db=db,
        )

        # Log conversation
        if customer:
            await conversation_service.create_conversation(
                db=db,
                customer_id=customer.id,
                channel=request.channel,
                direction="inbound",
                content=request.message,
                ai_generated=False,
            )

            # Log AI response
            await conversation_service.create_conversation(
                db=db,
                customer_id=customer.id,
                channel=request.channel,
                direction="outbound",
                content=response,
                ai_generated=True,
            )

        # Check for escalation
        conversation_history = await conversation_service.get_conversation_history(
            db=db, customer_id=customer.id if customer else None, limit=5
        )

        should_escalate, escalation_reason = await agent_service.check_escalation(
            message=request.message, conversation_history=[c.to_dict() for c in conversation_history]
        )

        return {
            "success": True,
            "response": response,
            "escalated": should_escalate,
            "escalation_reason": escalation_reason if should_escalate else None,
        }

    except Exception as e:
        logger.error(f"❌ Error processing chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat: {str(e)}",
        )


@router.post("/test", status_code=status.HTTP_200_OK)
async def test_agent(
    message: str,
    channel: str = "web",
):
    """
    Test the agent without database (simple endpoint)

    Args:
        message: Test message
        channel: Channel for response style

    Returns:
        Agent response
    """
    try:
        response = await agent_service.process_customer_message(
            message=message,
            channel=channel,
            customer_context=None,
            db=None,
        )

        return {
            "success": True,
            "message": message,
            "channel": channel,
            "response": response,
        }

    except Exception as e:
        logger.error(f"❌ Error testing agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error testing agent: {str(e)}",
        )


@router.get("/status", status_code=status.HTTP_200_OK)
async def get_agent_status():
    """
    Get agent operational status

    Returns:
        Agent status information
    """
    return {
        "status": "operational",
        "agent": "Nur Scents Assistant",
        "model": "gemini-2.0-flash-exp",
        "channels_supported": ["whatsapp", "email", "web"],
        "capabilities": [
            "product_search",
            "product_recommendations",
            "order_creation",
            "order_status_check",
            "faq_answers",
            "escalation_detection",
        ],
    }
