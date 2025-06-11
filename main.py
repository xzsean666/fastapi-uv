"""Entry point for running the FastAPI application with uvicorn."""

import uvicorn

from app.config import settings


def main():
    """Run the FastAPI application."""
    uvicorn.run(
        "app.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info" if not settings.debug else "debug",
    )


if __name__ == "__main__":
    main()
