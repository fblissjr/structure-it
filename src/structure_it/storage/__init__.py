"""Storage backends for structured data."""

from structure_it.storage.base import BaseStorage, StoredEntity
from structure_it.storage.duckdb_storage import DuckDBStorage
from structure_it.storage.json_storage import JSONStorage

__all__ = [
    "BaseStorage",
    "StoredEntity",
    "JSONStorage",
    "DuckDBStorage",
]
