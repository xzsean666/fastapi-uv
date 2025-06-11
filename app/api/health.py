"""Health check and system routes."""

from fastapi import APIRouter

from app.config import settings
from app.models import HealthResponse, MessageResponse

router = APIRouter()


@router.get("/", response_model=MessageResponse)
async def root():
    """Root endpoint."""
    return MessageResponse(
        message=f"Welcome to {settings.app_name}",
        data={"version": settings.app_version},
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy", version=settings.app_version, service=settings.app_name
    )
