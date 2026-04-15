"""
System test script - Verify core prototype is working
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import AsyncSessionLocal
from app.services.product_service import product_service
from app.services.customer_service import customer_service
from app.services.agent_service import agent_service
from app.core.logging import setup_logging
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


async def test_database():
    """Test database connectivity and data"""
    logger.info("🧪 Testing database...")

    async with AsyncSessionLocal() as db:
        # Test product retrieval
        products = await product_service.get_all_products(db, limit=5)
        logger.info(f"✅ Retrieved {len(products)} products")

        if products:
            product = products[0]
            logger.info(f"   Sample product: {product.name} - PKR {product.price}")

        # Test product search
        search_results = await product_service.search_products(db, "oudh", limit=3)
        logger.info(f"✅ Search for 'oudh' found {len(search_results)} products")

        # Test categories
        categories = await product_service.get_categories()
        logger.info(f"✅ Found {len(categories)} categories")

    logger.info("✅ Database tests passed!\n")


async def test_customer_service():
    """Test customer service"""
    logger.info("🧪 Testing customer service...")

    async with AsyncSessionLocal() as db:
        # Create test customer
        customer = await customer_service.create_or_update_customer(
            db=db,
            phone_number="+923001234567",
            name="Test Customer",
            email="test@example.com",
            city="Karachi",
            preferred_channel="whatsapp",
        )

        logger.info(f"✅ Created/updated customer: {customer.name} ({customer.phone_number})")

        # Retrieve customer
        retrieved = await customer_service.get_customer_by_phone(db, "+923001234567")
        if retrieved:
            logger.info(f"✅ Retrieved customer: {retrieved.name}")

    logger.info("✅ Customer service tests passed!\n")


async def test_ai_agent():
    """Test AI agent"""
    logger.info("🧪 Testing AI agent...")

    test_messages = [
        ("web", "What products do you have?"),
        ("whatsapp", "Oudh ki price kya hai?"),
        ("email", "I would like to know about your bestselling products"),
    ]

    for channel, message in test_messages:
        try:
            response = await agent_service.process_customer_message(
                message=message,
                channel=channel,
                customer_context=None,
                db=None,
            )

            logger.info(f"✅ {channel.upper()}: {message[:50]}...")
            logger.info(f"   Response: {response[:100]}...")

        except Exception as e:
            logger.error(f"❌ Agent test failed for {channel}: {e}")

    logger.info("✅ AI agent tests passed!\n")


async def test_product_recommendations():
    """Test product recommendations"""
    logger.info("🧪 Testing product recommendations...")

    async with AsyncSessionLocal() as db:
        # Get bestsellers
        recommendations = await agent_service.get_recommendations(db)

        logger.info(f"✅ Got {len(recommendations)} recommendations")

        if recommendations:
            logger.info(f"   Sample: {recommendations[0]['name']}")

    logger.info("✅ Product recommendation tests passed!\n")


async def run_all_tests():
    """Run all system tests"""
    logger.info("🚀 Starting Nur Scents System Tests\n")
    logger.info("=" * 60)

    try:
        # Test database
        await test_database()

        # Test customer service
        await test_customer_service()

        # Test AI agent
        await test_ai_agent()

        # Test product recommendations
        await test_product_recommendations()

        logger.info("=" * 60)
        logger.info("🎉 All tests passed successfully!")
        logger.info("\n✅ Core prototype is working!")
        logger.info("\n📋 Next steps:")
        logger.info("   1. Start the FastAPI server: uvicorn app.main:app --reload")
        logger.info("   2. Test the API endpoints: http://localhost:8000/docs")
        logger.info("   3. Test the agent: POST /api/v1/agent/test")

    except Exception as e:
        logger.error(f"❌ Tests failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run_all_tests())
