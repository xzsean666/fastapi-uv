"""FastAPI dependencies for the application."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

# Create rate limiter instance
limiter = Limiter(key_func=get_remote_address)


def get_limiter():
    """Get the rate limiter instance."""
    return limiter


def create_rate_limit_dependency(requests: int = None, period: int = None):
    """Create a rate limit dependency with custom limits.

    Args:
        requests: Number of requests allowed (default from settings)
        period: Time period in seconds (default from settings)

    Returns:
        A dependency function that can be used with FastAPI
    """
    requests = requests or settings.rate_limit_requests
    period = period or settings.rate_limit_period

    async def rate_limit_check(request: Request):
        """Check rate limit for the current request."""
        # This is a placeholder - actual rate limiting is handled by slowapi middleware
        return True

    return rate_limit_check


# Common rate limit dependencies
RateLimitDep = Annotated[bool, Depends(create_rate_limit_dependency())]
StrictRateLimitDep = Annotated[
    bool, Depends(create_rate_limit_dependency(requests=10, period=60))
]


async def verify_api_key(request: Request) -> str:
    """Verify API key from request headers (example dependency)."""
    api_key = request.headers.get("X-API-Key")
    if settings.debug:
        # In debug mode, allow requests without API key
        return api_key or "debug-key"

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Here you would typically verify the API key against a database
    # For now, we'll just return it
    return api_key


# API key dependency
ApiKeyDep = Annotated[str, Depends(verify_api_key)]
