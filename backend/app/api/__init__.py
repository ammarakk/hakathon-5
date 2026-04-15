"""
Nur Scents Customer Success Agent - API Routes
"""

from fastapi import APIRouter
from app.api.endpoints import health, products, orders, webhook, agent, mcp

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(webhook.router, prefix="/webhook", tags=["webhooks"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
