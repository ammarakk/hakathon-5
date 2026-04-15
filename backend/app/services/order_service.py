"""
Order service
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.order import Order, OrderItem
from app.models.product import Product
from datetime import datetime, timedelta
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class OrderService:
    """Service for order-related operations"""

    async def create_order(
        self,
        db: AsyncSession,
        customer_id: int,
        products_data: List[dict],
        address: str,
        city: str,
        payment_method: str,
        channel: str = "web",
        source_message_id: Optional[str] = None,
    ) -> Order:
        """
        Create a new order

        Args:
            db: Database session
            customer_id: Customer ID
            products_data: List of product items with product_id, quantity, size
            address: Delivery address
            city: Delivery city
            payment_method: Payment method
            channel: Order channel (whatsapp, email, web)
            source_message_id: Original message ID from channel

        Returns:
            Created order
        """
        # Generate order number
        order_number = f"NS-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Calculate total amount and delivery charges
        subtotal = 0
        order_items = []

        for item_data in products_data:
            product_id = item_data.get("product_id")
            quantity = item_data.get("quantity", 1)
            size = item_data.get("size")

            # Get product
            product = await db.execute(
                select(Product).where(Product.id == product_id)
            )
            product = product.scalar_one_or_none()

            if not product:
                raise ValueError(f"Product {product_id} not found")

            if product.stock < quantity:
                raise ValueError(
                    f"Product {product.name} has only {product.stock} items available"
                )

            price_per_unit = product.price
            item_subtotal = price_per_unit * quantity

            order_items.append(
                {
                    "product_id": product_id,
                    "product_name": product.name,
                    "quantity": quantity,
                    "price_per_unit": price_per_unit,
                    "size": size,
                    "subtotal": item_subtotal,
                }
            )

            subtotal += item_subtotal

        # Calculate delivery charges
        delivery_charges = 0
        if subtotal < 15000:
            if city.lower() == "karachi":
                delivery_charges = 150
            else:
                delivery_charges = 250

        total_amount = subtotal + delivery_charges

        # Calculate expected delivery date
        if city.lower() == "karachi":
            expected_days = 3
        else:
            expected_days = 5

        expected_delivery = datetime.now() + timedelta(days=expected_days)

        # Create order
        order = Order(
            order_number=order_number,
            customer_id=customer_id,
            total_amount=total_amount,
            payment_method=payment_method,
            payment_status="pending",
            delivery_address=address,
            delivery_city=city,
            delivery_charges=delivery_charges,
            expected_delivery_date=expected_delivery,
            channel=channel,
            source_message_id=source_message_id,
            status="pending",
        )

        db.add(order)
        await db.flush()

        # Create order items
        for item_data in order_items:
            order_item = OrderItem(
                order_id=order.id,
                **item_data
            )
            db.add(order_item)

            # Update product stock
            product = await db.execute(
                select(Product).where(Product.id == item_data["product_id"])
            )
            product = product.scalar_one_or_none()
            if product:
                product.stock -= item_data["quantity"]

        await db.commit()
        await db.refresh(order)

        logger.info(f"✅ Created order {order_number} for customer {customer_id}")

        return order

    async def get_order_by_id(
        self, db: AsyncSession, order_id: int
    ) -> Optional[Order]:
        """
        Get order by ID

        Args:
            db: Database session
            order_id: Order ID

        Returns:
            Order or None
        """
        query = select(Order).where(Order.id == order_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_order_by_number(
        self, db: AsyncSession, order_number: str
    ) -> Optional[Order]:
        """
        Get order by order number

        Args:
            db: Database session
            order_number: Order number

        Returns:
            Order or None
        """
        query = select(Order).where(Order.order_number == order_number)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update_order_status(
        self, db: AsyncSession, order_number: str, status: str
    ) -> Optional[Order]:
        """
        Update order status

        Args:
            db: Database session
            order_number: Order number
            status: New status

        Returns:
            Updated order or None
        """
        order = await self.get_order_by_number(db, order_number)

        if order:
            order.status = status

            if status == "delivered":
                order.actual_delivery_date = datetime.now()

            await db.commit()
            await db.refresh(order)

            logger.info(f"✅ Updated order {order_number} status to {status}")

        return order

    async def get_customer_orders(
        self,
        db: AsyncSession,
        customer_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> List[Order]:
        """
        Get customer's orders

        Args:
            db: Database session
            customer_id: Customer ID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of orders
        """
        query = (
            select(Order)
            .where(Order.customer_id == customer_id)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(query)
        return list(result.scalars().all())


# Global service instance
order_service = OrderService()
