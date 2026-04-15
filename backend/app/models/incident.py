"""
Incident model for escalated issues
"""

from sqlalchemy import Column, Integer, String, DateTime, String, ForeignKey
from sqlalchemy.sql import func
from app.models.database import Base


class Incident(Base):
    """Incident model for escalated issues requiring human intervention"""

    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    type = Column(String(50))  # complaint, return, refund, technical, other
    severity = Column(String(20))  # low, medium, high, urgent
    status = Column(String(50), default="open")  # open, in_progress, resolved, closed
    description = Column(String, nullable=False)
    resolution = Column(String)
    assigned_to = Column(String(100))  # NULL = AI handled, otherwise owner name
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime)
    metadata = Column(String, default={})

    def __repr__(self):
        return f"<Incident(id={self.id}, type={self.type}, status={self.status})>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "conversation_id": self.conversation_id,
            "type": self.type,
            "severity": self.severity,
            "status": self.status,
            "description": self.description,
            "resolution": self.resolution,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "metadata": self.metadata or {},
        }
