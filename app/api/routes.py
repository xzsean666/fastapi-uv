"""API route aggregation."""

from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.kv_cache_api import router as kv_cache_router

# Create main router
router = APIRouter()

# Include all sub-routers
router.include_router(health_router)
router.include_router(auth_router)
router.include_router(kv_cache_router)
