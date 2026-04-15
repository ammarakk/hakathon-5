"""
Product model
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, DECIMAL, JSON
from sqlalchemy.sql import func
from app.models.database import Base


class Product(Base):
    """Product model"""

    __tablename__ = "products"

    id = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), index=True)
    description = Column(String)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=10)
    images = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    sizes = Column(JSON, default=list)
    bestseller = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    metadata = Column(JSON, default={})

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, price={self.price})>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "price": float(self.price) if self.price else 0,
            "stock": self.stock,
            "low_stock_threshold": self.low_stock_threshold,
            "images": self.images or [],
            "tags": self.tags or [],
            "sizes": self.sizes or [],
            "bestseller": self.bestseller,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata or {},
        }
