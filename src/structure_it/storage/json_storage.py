"""JSON file-based storage backend."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from structure_it.storage.base import BaseStorage, StoredEntity


class JSONStorage(BaseStorage):
    """Storage backend using JSON files.

    Stores each entity as a separate JSON file in a directory structure.
    Simple, human-readable, good for prototyping and small datasets.
    """

    def __init__(self, base_path: str | Path = "./data/entities") -> None:
        """Initialize JSON storage.

        Args:
            base_path: Directory path for storing JSON files.
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _entity_path(self, entity_id: str) -> Path:
        """Get file path for an entity."""
        # Use first 2 chars of hash for subdirectory (sharding)
        subdir = self.base_path / entity_id[:2]
        subdir.mkdir(exist_ok=True)
        return subdir / f"{entity_id}.json"

    async def store_entity(
        self,
        entity_id: str,
        source_type: str,
        source_url: str,
        raw_content: str,
        structured_data: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Store an entity as a JSON file."""
        entity_data = {
            "entity_id": entity_id,
            "source_type": source_type,
            "source_url": source_url,
            "raw_content": raw_content,
            "structured_data": structured_data,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
        }

        path = self._entity_path(entity_id)
        with open(path, "w") as f:
            json.dump(entity_data, f, indent=2)

    async def get_entity(self, entity_id: str) -> StoredEntity | None:
        """Retrieve an entity from JSON file."""
        path = self._entity_path(entity_id)

        if not path.exists():
            return None

        with open(path, "r") as f:
            data = json.load(f)

        return StoredEntity(**data)

    async def query_entities(
        self,
        source_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[StoredEntity]:
        """Query entities by scanning JSON files."""
        entities: list[StoredEntity] = []

        # Scan all JSON files
        for json_file in self.base_path.rglob("*.json"):
            with open(json_file, "r") as f:
                data = json.load(f)

            # Filter by source_type if specified
            if source_type and data.get("source_type") != source_type:
                continue

            entities.append(StoredEntity(**data))

        # Sort by created_at (newest first)
        entities.sort(key=lambda e: e.created_at, reverse=True)

        # Apply pagination
        return entities[offset : offset + limit]

    async def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity JSON file."""
        path = self._entity_path(entity_id)

        if not path.exists():
            return False

        path.unlink()
        return True

    async def count_entities(self, source_type: str | None = None) -> int:
        """Count entities by scanning JSON files."""
        count = 0

        for json_file in self.base_path.rglob("*.json"):
            if source_type:
                with open(json_file, "r") as f:
                    data = json.load(f)
                if data.get("source_type") == source_type:
                    count += 1
            else:
                count += 1

        return count
