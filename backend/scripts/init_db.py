"""
Database initialization script
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import engine, AsyncSessionLocal, init_db
from app.services.product_service import product_service
from app.core.logging import setup_logging
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


async def initialize_database():
    """Initialize database with tables and product data"""

    try:
        logger.info("🔧 Starting database initialization...")

        # Initialize database tables
        await init_db()
        logger.info("✅ Database tables created")

        # Create async session
        async with AsyncSessionLocal() as db:
            # Initialize products from JSON
            count = await product_service.initialize_products_from_json(db)
            logger.info(f"✅ Initialized {count} products in database")

        logger.info("🎉 Database initialization complete!")

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


async def verify_database():
    """Verify database has data"""

    try:
        logger.info("🔍 Verifying database...")

        async with AsyncSessionLocal() as db:
            # Check products
            products = await product_service.get_all_products(db)
            logger.info(f"✅ Found {len(products)} products in database")

            # Check categories
            categories = await product_service.get_categories()
            logger.info(f"✅ Found {len(categories)} categories")

        logger.info("✅ Database verification complete!")

    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        raise


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Nur Scents Database Initialization")
    parser.add_argument("--verify", action="store_true", help="Verify database only")

    args = parser.parse_args()

    if args.verify:
        asyncio.run(verify_database())
    else:
        asyncio.run(initialize_database())
        asyncio.run(verify_database())
