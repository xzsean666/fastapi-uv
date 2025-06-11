"""Pydantic models for request/response validation."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(default="healthy", description="Service health status")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Current timestamp"
    )
    version: str = Field(description="Application version")
    service: str = Field(description="Service name")


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    detail: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional error details"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Error timestamp"
    )


class MessageResponse(BaseModel):
    """Simple message response model."""

    message: str = Field(description="Response message")
    data: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional response data"
    )


class ExampleRequest(BaseModel):
    """Example request model."""

    name: str = Field(..., min_length=1, max_length=100, description="Name field")
    age: Optional[int] = Field(default=None, ge=0, le=150, description="Age field")
    email: Optional[str] = Field(
        default=None, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", description="Email field"
    )


class ExampleResponse(BaseModel):
    """Example response model."""

    id: int = Field(description="Unique identifier")
    name: str = Field(description="Name field")
    age: Optional[int] = Field(default=None, description="Age field")
    email: Optional[str] = Field(default=None, description="Email field")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
