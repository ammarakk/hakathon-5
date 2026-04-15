"""
Health Check Endpoint
"""

from fastapi import APIRouter, status
from typing import Dict, Any

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint

    Returns:
        Health status of the service
    """
    return {
        "status": "healthy",
        "service": "nur-scents-agent",
        "version": "0.1.0",
    }


@router.get("/ping", status_code=status.HTTP_200_OK)
async def ping() -> Dict[str, str]:
    """
    Simple ping endpoint

    Returns:
        Pong response
    """
    return {"message": "pong"}
