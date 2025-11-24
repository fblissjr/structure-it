"""Storage backends for structured data."""

from structure_it.storage.base import BaseStorage, StoredEntity
from structure_it.storage.duckdb_storage import DuckDBStorage
from structure_it.storage.json_storage import JSONStorage
from structure_it.storage.star_schema_storage import StarSchemaStorage

__all__ = [
    "BaseStorage",
    "StoredEntity",
    "JSONStorage",
    "DuckDBStorage",
    "StarSchemaStorage",
]