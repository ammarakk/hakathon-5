"""
Products Endpoint
"""

from fastapi import APIRouter, status, HTTPException
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_products(
    category: Optional[str] = None,
    bestseller: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Get all products with optional filters

    Args:
        category: Filter by category
        bestseller: Filter by bestseller status
        min_price: Minimum price
        max_price: Maximum price

    Returns:
        List of products
    """
    try:
        # Load products data
        products_path = Path("./data/nur_scents_products.json")
        if not products_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Products data file not found"
            )

        with open(products_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        products = data.get("products", [])

        # Apply filters
        if category:
            products = [p for p in products if p.get("category") == category]

        if bestseller is not None:
            products = [p for p in products if p.get("bestseller") == bestseller]

        if min_price is not None:
            products = [p for p in products if p.get("price", 0) >= min_price]

        if max_price is not None:
            products = [p for p in products if p.get("price", 0) <= max_price]

        return {
            "success": True,
            "count": len(products),
            "products": products,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading products: {str(e)}"
        )


@router.get("/{product_id}", status_code=status.HTTP_200_OK)
async def get_product(product_id: str) -> Dict[str, Any]:
    """
    Get a specific product by ID

    Args:
        product_id: Product ID (e.g., NS-001)

    Returns:
        Product details
    """
    try:
        # Load products data
        products_path = Path("./data/nur_scents_products.json")
        if not products_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Products data file not found"
            )

        with open(products_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        products = data.get("products", [])

        # Find product by ID
        product = next((p for p in products if p.get("id") == product_id), None)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )

        return {
            "success": True,
            "product": product,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading product: {str(e)}"
        )


@router.get("/categories/list", status_code=status.HTTP_200_OK)
async def get_categories() -> Dict[str, Any]:
    """
    Get all product categories

    Returns:
        List of categories
    """
    try:
        # Load products data
        products_path = Path("./data/nur_scents_products.json")
        if not products_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Products data file not found"
            )

        with open(products_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        categories = data.get("categories", [])

        return {
            "success": True,
            "categories": categories,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading categories: {str(e)}"
        )
