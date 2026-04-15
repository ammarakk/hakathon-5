"""
Customer model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, DECIMAL, JSON
from sqlalchemy.sql import func
from app.models.database import Base


class Customer(Base):
    """Customer model"""

    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255))
    email = Column(String(255), index=True)
    address = Column(String)
    city = Column(String(100))
    preferred_channel = Column(String(20), default="whatsapp")  # whatsapp, email, web
    language = Column(String(10), default="ur")  # ur (Roman Urdu), en
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    total_orders = Column(Integer, default=0)
    total_spent = Column(DECIMAL(10, 2), default=0)
    is_blacklisted = Column(Boolean, default=False)
    blacklist_reason = Column(String)
    metadata = Column(JSON, default={})

    def __repr__(self):
        return f"<Customer(id={self.id}, phone={self.phone_number}, name={self.name})>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "phone_number": self.phone_number,
            "name": self.name,
            "email": self.email,
            "address": self.address,
            "city": self.city,
            "preferred_channel": self.preferred_channel,
            "language": self.language,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "total_orders": self.total_orders,
            "total_spent": float(self.total_spent) if self.total_spent else 0,
            "is_blacklisted": self.is_blacklisted,
            "blacklist_reason": self.blacklist_reason,
            "metadata": self.metadata or {},
        }
