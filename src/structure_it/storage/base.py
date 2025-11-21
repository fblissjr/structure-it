"""Base storage interface for extracted entities."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class StoredEntity(BaseModel):
    """Representation of a stored entity.

    Attributes:
        entity_id: Unique identifier for the entity.
        source_type: Type of source (e.g., 'article', 'paper').
        source_url: Source URL or file path.
        raw_content: Original unstructured content.
        structured_data: Extracted structured data.
        metadata: Additional metadata.
        created_at: Timestamp of creation.
    """

    entity_id: str
    source_type: str
    source_url: str
    raw_content: str
    structured_data: dict[str, Any]
    metadata: dict[str, Any]
    created_at: datetime


class BaseStorage(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    async def store_entity(
        self,
        entity_id: str,
        source_type: str,
        source_url: str,
        raw_content: str,
        structured_data: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Store an extracted entity.

        Args:
            entity_id: Unique identifier (SHA256 hash).
            source_type: Type of source (e.g., 'academic_paper', 'article').
            source_url: URL or path of source document.
            raw_content: Original unstructured content.
            structured_data: Extracted structured data (Pydantic model as dict).
            metadata: Optional metadata (extraction config, model used, etc.).
        """
        pass

    @abstractmethod
    async def get_entity(self, entity_id: str) -> StoredEntity | None:
        """Retrieve an entity by ID.

        Args:
            entity_id: Unique identifier.

        Returns:
            StoredEntity if found, None otherwise.
        """
        pass

    @abstractmethod
    async def query_entities(
        self,
        source_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[StoredEntity]:
        """Query entities with optional filtering.

        Args:
            source_type: Filter by source type (optional).
            limit: Maximum number of results.
            offset: Number of results to skip.

        Returns:
            List of matching entities.
        """
        pass

    @abstractmethod
    async def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity by ID.

        Args:
            entity_id: Unique identifier.

        Returns:
            True if deleted, False if not found.
        """
        pass

    @abstractmethod
    async def count_entities(self, source_type: str | None = None) -> int:
        """Count entities, optionally filtered by type.

        Args:
            source_type: Filter by source type (optional).

        Returns:
            Number of matching entities.
        """
        pass
