"""
Product service
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from app.models.product import Product
from app.models.database import get_db
import json
import logging

logger = logging.getLogger(__name__)


class ProductService:
    """Service for product-related operations"""

    def __init__(self):
        self.products_data = None
        self._load_products_data()

    def _load_products_data(self):
        """Load products from JSON file"""
        try:
            with open("./data/nur_scents_products.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.products_data = data
                logger.info(f"✅ Loaded {len(data.get('products', []))} products from JSON")
        except Exception as e:
            logger.error(f"❌ Failed to load products data: {e}")
            self.products_data = {"products": [], "categories": []}

    async def get_all_products(
        self,
        db: AsyncSession,
        category: Optional[str] = None,
        bestseller: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Product]:
        """
        Get all products with optional filters

        Args:
            db: Database session
            category: Filter by category
            bestseller: Filter by bestseller status
            min_price: Minimum price
            max_price: Maximum price
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of products
        """
        query = select(Product).where(Product.is_active == True)

        # Apply filters
        if category:
            query = query.where(Product.category == category)

        if bestseller is not None:
            query = query.where(Product.bestseller == bestseller)

        if min_price is not None:
            query = query.where(Product.price >= min_price)

        if max_price is not None:
            query = query.where(Product.price <= max_price)

        # Apply pagination and ordering
        query = query.order_by(Product.name).offset(skip).limit(limit)

        result = await db.execute(query)
        products = result.scalars().all()

        return list(products)

    async def get_product_by_id(self, db: AsyncSession, product_id: str) -> Optional[Product]:
        """
        Get product by ID

        Args:
            db: Database session
            product_id: Product ID

        Returns:
            Product or None
        """
        query = select(Product).where(
            and_(Product.id == product_id, Product.is_active == True)
        )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def search_products(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 10,
    ) -> List[Product]:
        """
        Search products by name, description, or tags

        Args:
            db: Database session
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching products
        """
        search_pattern = f"%{query}%"

        # Search in name, description, and category
        db_query = select(Product).where(
            and_(
                Product.is_active == True,
                or_(
                    Product.name.ilike(search_pattern),
                    Product.description.ilike(search_pattern),
                    Product.category.ilike(search_pattern),
                )
            )
        ).limit(limit)

        result = await db.execute(db_query)
        return list(result.scalars().all())

    async def get_categories(self) -> List[dict]:
        """
        Get all product categories

        Returns:
            List of categories
        """
        if self.products_data:
            return self.products_data.get("categories", [])
        return []

    async def get_bestsellers(self, db: AsyncSession, limit: int = 5) -> List[Product]:
        """
        Get bestselling products

        Args:
            db: Database session
            limit: Maximum number of products

        Returns:
            List of bestselling products
        """
        query = (
            select(Product)
            .where(and_(Product.bestseller == True, Product.is_active == True))
            .order_by(Product.name)
            .limit(limit)
        )

        result = await db.execute(query)
        return list(result.scalars().all())

    async def check_stock(self, db: AsyncSession, product_id: str, quantity: int = 1) -> dict:
        """
        Check if product is in stock

        Args:
            db: Database session
            product_id: Product ID
            quantity: Required quantity

        Returns:
            Stock availability info
        """
        product = await self.get_product_by_id(db, product_id)

        if not product:
            return {
                "product_id": product_id,
                "in_stock": False,
                "can_fulfill": False,
                "message": "Product not found"
            }

        in_stock = product.stock >= quantity
        low_stock = product.stock <= product.low_stock_threshold

        return {
            "product_id": product_id,
            "product_name": product.name,
            "requested_quantity": quantity,
            "available_stock": product.stock,
            "in_stock": in_stock,
            "can_fulfill": in_stock,
            "low_stock": low_stock,
            "message": (
                f"Only {product.stock} items available"
                if not in_stock
                else "In stock"
                if not low_stock
                else "Low stock"
            )
        }

    async def initialize_products_from_json(self, db: AsyncSession) -> int:
        """
        Initialize database with products from JSON file

        Args:
            db: Database session

        Returns:
            Number of products created/updated
        """
        if not self.products_data:
            return 0

        products_list = self.products_data.get("products", [])
        count = 0

        for product_data in products_list:
            # Check if product exists
            product = await self.get_product_by_id(db, product_data["id"])

            if product:
                # Update existing product
                for key, value in product_data.items():
                    if key != "id" and hasattr(product, key):
                        setattr(product, key, value)
            else:
                # Create new product
                product = Product(**product_data)
                db.add(product)

            count += 1

        await db.commit()
        logger.info(f"✅ Initialized {count} products in database")

        return count


# Global service instance
product_service = ProductService()
