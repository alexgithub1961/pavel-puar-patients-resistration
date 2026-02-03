"""Health check endpoint."""

from datetime import UTC, datetime

from fastapi import APIRouter

from src.core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint with configuration info."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/ready")
async def readiness_check() -> dict:
    """Readiness check for Kubernetes."""
    return {
        "status": "ready",
        "timestamp": datetime.now(UTC).isoformat(),
    }
