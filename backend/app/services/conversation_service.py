"""
Conversation service for tracking customer interactions
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from typing import List, Optional, Dict
from app.models.conversation import Conversation
from app.models.customer import Customer
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for conversation tracking"""

    async def create_conversation(
        self,
        db: AsyncSession,
        customer_id: Optional[int],
        channel: str,
        direction: str,
        content: str,
        channel_message_id: Optional[str] = None,
        ai_generated: bool = False,
        message_type: str = "text",
    ) -> Conversation:
        """
        Create a new conversation record

        Args:
            db: Database session
            customer_id: Customer ID
            channel: Communication channel
            direction: Message direction (inbound/outbound)
            content: Message content
            channel_message_id: Original message ID from channel
            ai_generated: Whether message was AI-generated
            message_type: Type of message

        Returns:
            Created conversation
        """
        conversation = Conversation(
            customer_id=customer_id,
            channel=channel,
            channel_message_id=channel_message_id,
            direction=direction,
            message_type=message_type,
            content=content,
            ai_generated=ai_generated,
        )

        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

        logger.info(
            f"✅ Created conversation: {channel} - {direction} (AI: {ai_generated})"
        )

        return conversation

    async def get_conversation_history(
        self,
        db: AsyncSession,
        customer_id: Optional[int] = None,
        phone_number: Optional[str] = None,
        limit: int = 10,
    ) -> List[Conversation]:
        """
        Get conversation history for a customer

        Args:
            db: Database session
            customer_id: Customer ID
            phone_number: Customer phone number (alternative)
            limit: Maximum number of conversations

        Returns:
            List of conversations
        """
        # If phone number provided, get customer ID first
        if phone_number and not customer_id:
            from app.services.customer_service import customer_service

            customer = await customer_service.get_customer_by_phone(db, phone_number)
            if customer:
                customer_id = customer.id

        if not customer_id:
            return []

        query = (
            select(Conversation)
            .where(Conversation.customer_id == customer_id)
            .order_by(desc(Conversation.created_at))
            .limit(limit)
        )

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_recent_conversations(
        self, db: AsyncSession, channel: Optional[str] = None, limit: int = 50
    ) -> List[Conversation]:
        """
        Get recent conversations

        Args:
            db: Database session
            channel: Filter by channel
            limit: Maximum number of conversations

        Returns:
            List of conversations
        """
        query = select(Conversation).order_by(desc(Conversation.created_at)).limit(
            limit
        )

        if channel:
            query = query.where(Conversation.channel == channel)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def mark_as_escalated(
        self, db: AsyncSession, conversation_id: int, reason: str
    ) -> Optional[Conversation]:
        """
        Mark conversation as escalated

        Args:
            db: Database session
            conversation_id: Conversation ID
            reason: Escalation reason

        Returns:
            Updated conversation or None
        """
        query = select(Conversation).where(Conversation.id == conversation_id)
        result = await db.execute(query)
        conversation = result.scalar_one_or_none()

        if conversation:
            conversation.escalated = True
            conversation.escalation_reason = reason
            await db.commit()
            await db.refresh(conversation)

            logger.info(f"⚠️ Conversation {conversation_id} escalated: {reason}")

        return conversation

    async def get_conversation_stats(
        self, db: AsyncSession, days: int = 7
    ) -> Dict[str, int]:
        """
        Get conversation statistics

        Args:
            db: Database session
            days: Number of days to look back

        Returns:
            Statistics dictionary
        """
        from sqlalchemy import func, date

        # Calculate date threshold
        threshold_date = datetime.now() - datetime.timedelta(days=days)

        # Total conversations
        total_query = (
            select(func.count(Conversation.id))
            .where(Conversation.created_at >= threshold_date)
            .where(Conversation.direction == "inbound")
        )
        total_result = await db.execute(total_query)
        total = total_result.scalar() or 0

        # AI-generated responses
        ai_query = (
            select(func.count(Conversation.id))
            .where(Conversation.created_at >= threshold_date)
            .where(Conversation.ai_generated == True)
        )
        ai_result = await db.execute(ai_query)
        ai_count = ai_result.scalar() or 0

        # Escalated conversations
        escalated_query = (
            select(func.count(Conversation.id))
            .where(Conversation.created_at >= threshold_date)
            .where(Conversation.escalated == True)
        )
        escalated_result = await db.execute(escalated_query)
        escalated_count = escalated_result.scalar() or 0

        # By channel
        channel_query = (
            select(
                Conversation.channel, func.count(Conversation.id).label("count")
            )
            .where(Conversation.created_at >= threshold_date)
            .where(Conversation.direction == "inbound")
            .group_by(Conversation.channel)
        )
        channel_result = await db.execute(channel_query)
        channel_counts = {row[0]: row[1] for row in channel_result.all()}

        return {
            "total_conversations": total,
            "ai_responses": ai_count,
            "escalated_conversations": escalated_count,
            "ai_percentage": round((ai_count / total * 100) if total > 0 else 0, 2),
            "by_channel": channel_counts,
            "days": days,
        }


# Global service instance
conversation_service = ConversationService()
