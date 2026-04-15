"""
Order models
"""

from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base


class Order(Base):
    """Order model"""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    status = Column(String(50), default="pending")  # pending, confirmed, processing, shipped, delivered, cancelled
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(String(50))
    payment_status = Column(String(50), default="pending")  # pending, paid, failed, refunded
    delivery_address = Column(String)
    delivery_city = Column(String(100))
    delivery_charges = Column(DECIMAL(10, 2), default=0)
    expected_delivery_date = Column(DateTime)
    actual_delivery_date = Column(DateTime)
    tracking_number = Column(String(100))
    channel = Column(String(20), nullable=False)  # whatsapp, email, web
    source_message_id = Column(String(255))  # ID from original channel message
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    metadata = Column(JSON, default={})

    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(number={self.order_number}, status={self.status}, amount={self.total_amount})>"

    def to_dict(self, include_items=True):
        """Convert model to dictionary"""
        result = {
            "id": self.id,
            "order_number": self.order_number,
            "customer_id": self.customer_id,
            "status": self.status,
            "total_amount": float(self.total_amount) if self.total_amount else 0,
            "payment_method": self.payment_method,
            "payment_status": self.payment_status,
            "delivery_address": self.delivery_address,
            "delivery_city": self.delivery_city,
            "delivery_charges": float(self.delivery_charges) if self.delivery_charges else 0,
            "expected_delivery_date": self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            "actual_delivery_date": self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            "tracking_number": self.tracking_number,
            "channel": self.channel,
            "source_message_id": self.source_message_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata or {},
        }

        if include_items:
            result["items"] = [item.to_dict() for item in self.items]

        return result


class OrderItem(Base):
    """Order item model"""

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(String(20), ForeignKey("products.id"))
    product_name = Column(String(255))
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(DECIMAL(10, 2), nullable=False)
    size = Column(String(50))
    subtotal = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="items")

    def __repr__(self):
        return f"<OrderItem(id={self.id}, product={self.product_name}, qty={self.quantity})>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "price_per_unit": float(self.price_per_unit) if self.price_per_unit else 0,
            "size": self.size,
            "subtotal": float(self.subtotal) if self.subtotal else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
