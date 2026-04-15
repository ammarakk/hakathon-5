"""
Customer service
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models.customer import Customer
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CustomerService:
    """Service for customer-related operations"""

    async def get_customer_by_id(
        self, db: AsyncSession, customer_id: int
    ) -> Optional[Customer]:
        """
        Get customer by ID

        Args:
            db: Database session
            customer_id: Customer ID

        Returns:
            Customer or None
        """
        query = select(Customer).where(Customer.id == customer_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_customer_by_phone(
        self, db: AsyncSession, phone_number: str
    ) -> Optional[Customer]:
        """
        Get customer by phone number

        Args:
            db: Database session
            phone_number: Phone number

        Returns:
            Customer or None
        """
        # Normalize phone number (remove spaces, dashes)
        normalized_phone = phone_number.replace(" ", "").replace("-", "")

        query = select(Customer).where(Customer.phone_number == normalized_phone)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_customer_by_email(
        self, db: AsyncSession, email: str
    ) -> Optional[Customer]:
        """
        Get customer by email

        Args:
            db: Database session
            email: Email address

        Returns:
            Customer or None
        """
        query = select(Customer).where(Customer.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def create_or_update_customer(
        self,
        db: AsyncSession,
        phone_number: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        preferred_channel: str = "whatsapp",
        language: str = "ur",
    ) -> Customer:
        """
        Create new customer or update existing one

        Args:
            db: Database session
            phone_number: Customer phone number
            name: Customer name
            email: Customer email
            address: Customer address
            city: Customer city
            preferred_channel: Preferred communication channel
            language: Preferred language

        Returns:
            Customer object
        """
        # Normalize phone number
        normalized_phone = phone_number.replace(" ", "").replace("-", "")

        # Try to get existing customer
        customer = await self.get_customer_by_phone(db, normalized_phone)

        if customer:
            # Update existing customer
            if name and not customer.name:
                customer.name = name
            if email and not customer.email:
                customer.email = email
            if address and not customer.address:
                customer.address = address
            if city and not customer.city:
                customer.city = city
            customer.preferred_channel = preferred_channel
            customer.language = language

            logger.info(f"✅ Updated customer: {normalized_phone}")
        else:
            # Create new customer
            customer = Customer(
                phone_number=normalized_phone,
                name=name,
                email=email,
                address=address,
                city=city,
                preferred_channel=preferred_channel,
                language=language,
            )
            db.add(customer)
            await db.flush()

            logger.info(f"✅ Created new customer: {normalized_phone}")

        await db.commit()
        await db.refresh(customer)

        return customer

    async def update_customer_stats(
        self, db: AsyncSession, customer_id: int, order_amount: float
    ) -> None:
        """
        Update customer statistics after order

        Args:
            db: Database session
            customer_id: Customer ID
            order_amount: Order amount
        """
        customer = await self.get_customer_by_id(db, customer_id)

        if customer:
            customer.total_orders += 1
            customer.total_spent += order_amount
            await db.commit()


# Global service instance
customer_service = CustomerService()
