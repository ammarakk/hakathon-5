"""
Products Endpoint - Updated with database integration
"""

from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.services.product_service import product_service
from app.schemas.product import ProductResponse, ProductListResponse

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK, response_model=ProductListResponse)
async def get_products(
    db: AsyncSession = Depends(get_db),
    category: Optional[str] = None,
    bestseller: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all products with optional filters

    Args:
        db: Database session
        category: Filter by category
        bestseller: Filter by bestseller status
        min_price: Minimum price
        max_price: Maximum price
        skip: Number of records to skip
        limit: Maximum number of records

    Returns:
        List of products
    """
    try:
        products = await product_service.get_all_products(
            db=db,
            category=category,
            bestseller=bestseller,
            min_price=min_price,
            max_price=max_price,
            skip=skip,
            limit=limit,
        )

        return {
            "success": True,
            "count": len(products),
            "products": [p.to_dict() for p in products],
        }

    except Exception as e:
        logger.error(f"❌ Error loading products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading products: {str(e)}",
        )


@router.get("/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductResponse)
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific product by ID

    Args:
        product_id: Product ID (e.g., NS-001)
        db: Database session

    Returns:
        Product details
    """
    try:
        product = await product_service.get_product_by_id(db, product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found",
            )

        return {
            "success": True,
            "product": product.to_dict(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error loading product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading product: {str(e)}",
        )


@router.get("/categories/list", status_code=status.HTTP_200_OK)
async def get_categories():
    """
    Get all product categories

    Returns:
        List of categories
    """
    try:
        categories = await product_service.get_categories()

        return {
            "success": True,
            "categories": categories,
        }

    except Exception as e:
        logger.error(f"❌ Error loading categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading categories: {str(e)}",
        )


@router.get("/bestsellers/top", status_code=status.HTTP_200_OK, response_model=ProductListResponse)
async def get_bestsellers(
    db: AsyncSession = Depends(get_db),
    limit: int = 5,
):
    """
    Get bestselling products

    Args:
        db: Database session
        limit: Maximum number of products

    Returns:
        List of bestselling products
    """
    try:
        products = await product_service.get_bestsellers(db=db, limit=limit)

        return {
            "success": True,
            "count": len(products),
            "products": [p.to_dict() for p in products],
        }

    except Exception as e:
        logger.error(f"❌ Error loading bestsellers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading bestsellers: {str(e)}",
        )
