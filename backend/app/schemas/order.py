"""
Order schemas
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional


class OrderItemRequest(BaseModel):
    """Order item request schema"""
    product_id: str = Field(..., description="Product ID")
    quantity: int = Field(1, ge=1, description="Quantity")
    size: Optional[str] = Field(None, description="Product size")


class OrderRequest(BaseModel):
    """Order request schema"""
    customer_name: str = Field(..., min_length=2, description="Customer name")
    phone_number: str = Field(..., description="Customer phone number")
    email: Optional[str] = Field(None, description="Customer email")
    address: str = Field(..., min_length=10, description="Delivery address")
    city: str = Field(..., min_length=2, description="Delivery city")
    products: List[OrderItemRequest] = Field(..., min_items=1, description="Product list")
    payment_method: str = Field(..., description="Payment method")

    @validator("payment_method")
    def validate_payment_method(cls, v):
        """Validate payment method"""
        valid_methods = ["Cash on Delivery", "Bank Transfer", "EasyPaisa", "JazzCash"]
        if v not in valid_methods:
            raise ValueError(f"Payment method must be one of: {', '.join(valid_methods)}")
        return v


class OrderResponse(BaseModel):
    """Order response schema"""
    success: bool = True
    message: str
    order: dict


class OrderStatusResponse(BaseModel):
    """Order status response schema"""
    success: bool = True
    order: dict
