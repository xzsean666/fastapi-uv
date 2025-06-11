"""Example service with business logic separated from API endpoints."""

from datetime import datetime
from typing import Any, Dict, List

from app.models import ExampleRequest, ExampleResponse


class ExampleService:
    """Service class for example business logic."""

    def __init__(self):
        """Initialize the service."""
        # In a real application, you might inject dependencies here
        # such as database connections, external API clients, etc.
        self._counter = 0
        self._storage: List[ExampleResponse] = []

    async def get_example_data(self) -> Dict[str, Any]:
        """Get example data.

        Returns:
            Dictionary containing example data
        """
        # Simulate some business logic
        return {
            "items_count": len(self._storage),
            "last_id": self._counter,
            "timestamp": datetime.utcnow().isoformat(),
            "data": [
                {
                    "id": item.id,
                    "name": item.name,
                    "created_at": item.created_at.isoformat(),
                }
                for item in self._storage[-5:]  # Return last 5 items
            ],
        }

    async def create_example(self, data: ExampleRequest) -> ExampleResponse:
        """Create a new example item.

        Args:
            data: The request data

        Returns:
            The created example response
        """
        # Simulate creating a resource
        self._counter += 1

        response = ExampleResponse(
            id=self._counter,
            name=data.name,
            age=data.age,
            email=data.email,
            created_at=datetime.utcnow(),
        )

        # Store in memory (in real app, this would be database)
        self._storage.append(response)

        return response

    async def get_example_by_id(self, example_id: int) -> ExampleResponse | None:
        """Get an example by ID.

        Args:
            example_id: The ID to search for

        Returns:
            The example if found, None otherwise
        """
        for item in self._storage:
            if item.id == example_id:
                return item
        return None

    async def update_example(
        self, example_id: int, data: ExampleRequest
    ) -> ExampleResponse | None:
        """Update an existing example.

        Args:
            example_id: The ID of the example to update
            data: The new data

        Returns:
            The updated example if found, None otherwise
        """
        for i, item in enumerate(self._storage):
            if item.id == example_id:
                updated = ExampleResponse(
                    id=example_id,
                    name=data.name,
                    age=data.age,
                    email=data.email,
                    created_at=item.created_at,
                )
                self._storage[i] = updated
                return updated
        return None

    async def delete_example(self, example_id: int) -> bool:
        """Delete an example by ID.

        Args:
            example_id: The ID of the example to delete

        Returns:
            True if deleted, False if not found
        """
        for i, item in enumerate(self._storage):
            if item.id == example_id:
                del self._storage[i]
                return True
        return False
