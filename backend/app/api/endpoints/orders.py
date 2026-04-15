"""
Orders Endpoint
"""

from fastapi import APIRouter, status, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class OrderRequest(BaseModel):
    """Order request model"""
    customer_name: str
    phone_number: str
    email: str = None
    address: str
    city: str
    products: list
    payment_method: str
    total_amount: float


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderRequest) -> Dict[str, Any]:
    """
    Create a new order

    Args:
        order: Order details

    Returns:
        Created order details
    """
    try:
        # Generate order number
        order_number = f"NS-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # TODO: Save to database
        # For now, return mock response
        return {
            "success": True,
            "message": "Order created successfully",
            "order": {
                "order_number": order_number,
                "customer_name": order.customer_name,
                "phone_number": order.phone_number,
                "email": order.email,
                "address": order.address,
                "city": order.city,
                "products": order.products,
                "payment_method": order.payment_method,
                "total_amount": order.total_amount,
                "status": "pending",
                "created_at": datetime.now().isoformat(),
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating order: {str(e)}"
        )


@router.get("/{order_number}", status_code=status.HTTP_200_OK)
async def get_order(order_number: str) -> Dict[str, Any]:
    """
    Get order details by order number

    Args:
        order_number: Order number

    Returns:
        Order details
    """
    try:
        # TODO: Fetch from database
        # For now, return mock response
        return {
            "success": True,
            "order": {
                "order_number": order_number,
                "status": "processing",
                "message": "Order tracking feature coming soon"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching order: {str(e)}"
        )
