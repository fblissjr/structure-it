"""DuckDB storage backend with flexible JSON support."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import duckdb

from structure_it.storage.base import BaseStorage, StoredEntity


class DuckDBStorage(BaseStorage):
    """Storage backend using DuckDB.

    Uses a flexible schema with JSON columns for structured data.
    Good for analytical queries while maintaining schema flexibility.
    """

    def __init__(self, db_path: str | Path = "./data/structure_it.duckdb") -> None:
        """Initialize DuckDB storage.

        Args:
            db_path: Path to DuckDB database file.
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database connection
        self.conn = duckdb.connect(str(self.db_path))

        # Create schema
        self._create_schema()

    def _create_schema(self) -> None:
        """Create database schema if it doesn't exist."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS extracted_entities (
                entity_id VARCHAR(64) PRIMARY KEY,
                source_type VARCHAR NOT NULL,
                source_url VARCHAR NOT NULL,
                raw_content TEXT,
                structured_data JSON NOT NULL,
                metadata JSON,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for common queries
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_source_type
            ON extracted_entities(source_type)
        """)

        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at
            ON extracted_entities(created_at)
        """)

    async def store_entity(
        self,
        entity_id: str,
        source_type: str,
        source_url: str,
        raw_content: str,
        structured_data: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Store an entity in DuckDB."""
        self.conn.execute(
            """
            INSERT OR REPLACE INTO extracted_entities
            (entity_id, source_type, source_url, raw_content, structured_data, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                entity_id,
                source_type,
                source_url,
                raw_content,
                json.dumps(structured_data),
                json.dumps(metadata or {}),
            ],
        )

    async def get_entity(self, entity_id: str) -> StoredEntity | None:
        """Retrieve an entity from DuckDB."""
        result = self.conn.execute(
            """
            SELECT entity_id, source_type, source_url, raw_content,
                   structured_data, metadata, created_at
            FROM extracted_entities
            WHERE entity_id = ?
            """,
            [entity_id],
        ).fetchone()

        if not result:
            return None

        return StoredEntity(
            entity_id=result[0],
            source_type=result[1],
            source_url=result[2],
            raw_content=result[3],
            structured_data=json.loads(result[4]),
            metadata=json.loads(result[5]),
            created_at=result[6],
        )

    async def query_entities(
        self,
        source_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[StoredEntity]:
        """Query entities with optional filtering."""
        if source_type:
            query = """
                SELECT entity_id, source_type, source_url, raw_content,
                       structured_data, metadata, created_at
                FROM extracted_entities
                WHERE source_type = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            params = [source_type, limit, offset]
        else:
            query = """
                SELECT entity_id, source_type, source_url, raw_content,
                       structured_data, metadata, created_at
                FROM extracted_entities
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            params = [limit, offset]

        results = self.conn.execute(query, params).fetchall()

        return [
            StoredEntity(
                entity_id=row[0],
                source_type=row[1],
                source_url=row[2],
                raw_content=row[3],
                structured_data=json.loads(row[4]),
                metadata=json.loads(row[5]),
                created_at=row[6],
            )
            for row in results
        ]

    async def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity from DuckDB."""
        result = self.conn.execute(
            "DELETE FROM extracted_entities WHERE entity_id = ?", [entity_id]
        )
        return result.fetchone()[0] > 0

    async def count_entities(self, source_type: str | None = None) -> int:
        """Count entities in DuckDB."""
        if source_type:
            result = self.conn.execute(
                "SELECT COUNT(*) FROM extracted_entities WHERE source_type = ?",
                [source_type],
            )
        else:
            result = self.conn.execute("SELECT COUNT(*) FROM extracted_entities")

        return result.fetchone()[0]

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()

    def __del__(self) -> None:
        """Cleanup on deletion."""
        if hasattr(self, "conn"):
            self.conn.close()
