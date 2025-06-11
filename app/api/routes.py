"""API route aggregation."""

from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.examples import router as examples_router
from app.api.health import router as health_router

# Create main router
router = APIRouter()

# Include all sub-routers
router.include_router(health_router)
router.include_router(examples_router)
router.include_router(auth_router)
