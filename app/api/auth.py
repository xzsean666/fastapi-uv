"""Authentication and protected API endpoints."""

from fastapi import APIRouter, Depends

from app.config import settings
from app.dependencies import verify_api_key
from app.models import MessageResponse

router = APIRouter(prefix=settings.api_prefix, tags=["authentication"])


@router.get(
    "/protected",
    response_model=MessageResponse,
    summary="Protected endpoint example",
    description="Example endpoint that requires API key",
)
async def protected_endpoint(api_key: str = Depends(verify_api_key)):
    """Protected endpoint that requires API key."""
    return MessageResponse(
        message="Access granted to protected resource",
        data={"api_key": api_key[:8] + "..." if len(api_key) > 8 else api_key},
    )
