"""Example API endpoints."""

from fastapi import APIRouter, Request, status

from app.config import settings
from app.dependencies import RateLimitDep, limiter
from app.models import ExampleRequest, ExampleResponse, MessageResponse
from services.example_service import ExampleService

router = APIRouter(prefix=settings.api_prefix, tags=["examples"])


@router.get(
    "/example",
    response_model=MessageResponse,
    summary="Example GET endpoint",
    description="A simple example endpoint with rate limiting",
)
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def get_example(request: Request, _: RateLimitDep):
    """Example GET endpoint with rate limiting."""
    service = ExampleService()
    result = await service.get_example_data()
    return MessageResponse(message="Example data retrieved", data=result)


@router.post(
    "/example",
    response_model=ExampleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Example POST endpoint",
    description="Create a new example resource",
)
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def create_example(
    request: Request, data: ExampleRequest, _: RateLimitDep
) -> ExampleResponse:
    """Example POST endpoint with rate limiting."""
    service = ExampleService()
    result = await service.create_example(data)
    return result
