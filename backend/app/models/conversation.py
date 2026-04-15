"""
Conversation model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.models.database import Base


class Conversation(Base):
    """Conversation model for tracking customer interactions"""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    channel = Column(String(20), nullable=False)  # whatsapp, email, web
    channel_message_id = Column(String(255), unique=True)
    direction = Column(String(20), nullable=False)  # inbound, outbound
    message_type = Column(String(50))  # text, image, audio, video, document
    content = Column(String, nullable=False)
    ai_generated = Column(Boolean, default=False)
    escalated = Column(Boolean, default=False)
    escalation_reason = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(JSON, default={})

    def __repr__(self):
        return f"<Conversation(id={self.id}, channel={self.channel}, direction={self.direction})>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "channel": self.channel,
            "channel_message_id": self.channel_message_id,
            "direction": self.direction,
            "message_type": self.message_type,
            "content": self.content,
            "ai_generated": self.ai_generated,
            "escalated": self.escalated,
            "escalation_reason": self.escalation_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.metadata or {},
        }
