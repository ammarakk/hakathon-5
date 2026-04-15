"""
Product schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ProductResponse(BaseModel):
    """Product response schema"""
    success: bool = True
    product: dict


class ProductListResponse(BaseModel):
    """Product list response schema"""
    success: bool = True
    count: int
    products: List[dict]


class ProductSearchRequest(BaseModel):
    """Product search request schema"""
    query: str = Field(..., min_length=2, description="Search query")
    limit: int = Field(10, ge=1, le=50, description="Maximum results")


class StockCheckRequest(BaseModel):
    """Stock check request schema"""
    product_id: str = Field(..., description="Product ID")
    quantity: int = Field(1, ge=1, description="Required quantity")
