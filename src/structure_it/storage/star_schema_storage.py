"""Star Schema storage backend for LLM context retrieval."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import duckdb

from structure_it.storage.base import BaseStorage, StoredEntity
from structure_it.utils.hashing import generate_id


class StarSchemaStorage(BaseStorage):
    """Storage backend using Dimensional Context Model (Star Schema).

    This storage shreds structured documents into atomic 'fact_items'
    optimized for granular retrieval and LLM context assembly.
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

        # Enable VSS (Vector Similarity Search) if available, or just array functions
        # self.conn.execute("INSTALL vss; LOAD vss;") # Optional: Check if available first

        # Create schema
        self._create_schema()

    def _create_schema(self) -> None:
        """Create database schema from SQL file."""
        schema_path = Path(__file__).parent / "schemas" / "star_schema.sql"
        with open(schema_path) as f:
            self.conn.execute(f.read())

    def check_document_status(self, doc_id: str, content_hash: str) -> tuple[bool, bool]:
        """Check if a document is new or changed.

        Args:
            doc_id: Document ID.
            content_hash: Hash of the current content.

        Returns:
            Tuple of (is_new, has_changed).
        """
        result = self.conn.execute(
            "SELECT content_hash FROM dim_documents WHERE doc_id = ?", [doc_id]
        ).fetchone()

        if not result:
            return True, False  # New document

        existing_hash = result[0]
        if existing_hash != content_hash:
            return False, True  # Existing document, content changed

        return False, False  # Existing document, no change

    def _get_shredding_rules(self) -> dict[str, dict[str, str]]:
        """Define rules for shredding structured lists into atomic facts.
        
        Returns:
            Dictionary mapping list_key -> configuration.
        """
        return {
            # Policy Domain
            "requirements": {
                "item_type": "requirement",
                "content_field": "statement",
                "id_field": "requirement_id",
                "location_field": "source_section"
            },
            # Academic/Article Domain
            "sections": {
                "item_type": "section",
                "content_field": "content",
                "id_field": "heading", # Use heading as ID seed if available
                "location_field": "heading"
            },
            # Citizen Exploration / Civic Domain
            "agenda_items": {
                "item_type": "agenda_item",
                "content_field": "title", # Fallback logic will append description
                "id_field": "number",
                "location_field": "number"
            },
            "votes": {
                "item_type": "vote",
                "content_field": "motion",
                "id_field": "motion",
                "location_field": "result" 
            },
            "public_comments": {
                "item_type": "public_comment",
                "content_field": "text", # Assuming it's a list of strings or dicts with 'text'
                "id_field": None,
                "location_field": None
            }
        }

    async def store_entity(
        self,
        entity_id: str,
        source_type: str,
        source_url: str,
        raw_content: str,
        structured_data: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Store an entity by shredding it into dimensions and facts.

        Args:
            entity_id: Unique identifier.
            source_type: Type of source.
            source_url: Source URL.
            raw_content: Original content.
            structured_data: Extracted data.
            metadata: Additional metadata.
        """
        # Calculate content hash
        content_hash = generate_id(raw_content)
        
        # Check for changes
        is_new, has_changed = self.check_document_status(entity_id, content_hash)
        
        # Prepare metadata
        doc_metadata = metadata or {}
        
        # Identify shredding targets to exclude from metadata
        shredding_rules = self._get_shredding_rules()
        lists_to_shred = [k for k in structured_data.keys() if k in shredding_rules]

        # Add extra fields from structured_data to metadata for flexibility
        for k, v in structured_data.items():
            # Exclude large lists that we are about to shred
            if k not in lists_to_shred and k not in ["content", "paragraphs"]:
                doc_metadata[k] = v

        # 1. Store/Update Document Dimension
        title = structured_data.get("title") or structured_data.get("policy_title") or "Untitled"
        
        if is_new:
            self.conn.execute(
                """
                INSERT INTO dim_documents
                (doc_id, source_type, title, url, metadata, full_text_blob, content_hash, version, first_seen_at, last_extracted_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                [
                    entity_id,
                    source_type,
                    title,
                    source_url,
                    json.dumps(doc_metadata),
                    raw_content,
                    content_hash
                ],
            )
            # Log creation audit
            self.conn.execute(
                """
                INSERT INTO audit_document_changes (doc_id, change_type, new_content_hash, details)
                VALUES (?, 'create', ?, 'Initial extraction')
                """,
                [entity_id, content_hash]
            )
            
        elif has_changed:
            # Fetch current version
            current_version = self.conn.execute(
                "SELECT version FROM dim_documents WHERE doc_id = ?", [entity_id]
            ).fetchone()[0]
            
            # Get old hash
            old_hash = self.conn.execute(
                "SELECT content_hash FROM dim_documents WHERE doc_id = ?", [entity_id]
            ).fetchone()[0]

            self.conn.execute(
                """
                UPDATE dim_documents SET
                title = ?,
                metadata = ?,
                full_text_blob = ?,
                content_hash = ?,
                version = version + 1,
                last_extracted_at = CURRENT_TIMESTAMP
                WHERE doc_id = ?
                """,
                [
                    title,
                    json.dumps(doc_metadata),
                    raw_content,
                    content_hash,
                    entity_id
                ],
            )
            # Log update audit
            self.conn.execute(
                """
                INSERT INTO audit_document_changes (doc_id, change_type, old_content_hash, new_content_hash, details)
                VALUES (?, 'update', ?, ?, ?)
                """,
                [entity_id, old_hash, content_hash, f"Updated to version {current_version + 1}"]
            )
            
            # Delete old facts to replace with new ones
            self.conn.execute("DELETE FROM fact_items WHERE doc_id = ?", [entity_id])
            
        else:
            # No change, just update timestamp
            self.conn.execute(
                "UPDATE dim_documents SET last_extracted_at = CURRENT_TIMESTAMP WHERE doc_id = ?",
                [entity_id]
            )

        # 2. Store Fact Items (Generic Shredding)
        # Only re-shred if new or changed
        if is_new or has_changed:
            items_to_insert = []
            domain = structured_data.get("policy_type", source_type) # Default domain

            for list_key, rules in shredding_rules.items():
                if list_key in structured_data and isinstance(structured_data[list_key], list):
                    
                    for i, item in enumerate(structured_data[list_key]):
                        # Handle primitive lists (e.g. list of strings)
                        if isinstance(item, str):
                            content = item
                            props = {}
                            item_id_seed = f"{list_key}_{i}"
                            location = None
                        else:
                            # Handle dict items
                            content = item.get(rules["content_field"], "")
                            
                            # Append secondary content if available (e.g. description)
                            if "description" in item and item["description"]:
                                content += f" {item['description']}"
                                
                            # Properties: everything except the content field
                            props = {k: v for k, v in item.items() if k != rules["content_field"]}
                            
                            # ID Generation
                            seed = item.get(rules["id_field"]) if rules["id_field"] else None
                            item_id_seed = seed or f"{list_key}_{i}"
                            
                            # Location
                            location = item.get(rules["location_field"]) if rules["location_field"] else None

                        item_id = generate_id(entity_id, str(item_id_seed))
                        
                        # Placeholder embedding
                        embedding = [0.0] * 768

                        items_to_insert.append((
                            item_id,
                            entity_id,
                            domain,
                            rules["item_type"],
                            content,
                            embedding,
                            json.dumps(props),
                            location
                        ))

            # Batch Insert
            if items_to_insert:
                self.conn.executemany(
                    """
                    INSERT OR REPLACE INTO fact_items
                    (item_id, doc_id, domain, item_type, content_text, embedding, properties, location_pointer)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    items_to_insert
                )

    async def get_entity(self, entity_id: str) -> StoredEntity | None:
        """Retrieve an entity from DuckDB.

        Note: This reconstructs the entity from dim_documents.
        To get the full structured data back, we'd need to query fact_items and re-assemble.
        For now, we return the document level info.
        """
        result = self.conn.execute(
            """
            SELECT doc_id, source_type, url, full_text_blob,
                   metadata, created_at, title
            FROM dim_documents
            WHERE doc_id = ?
            """,
            [entity_id],
        ).fetchone()

        if not result:
            return None

        metadata = json.loads(result[4])

        # Attempt to reconstruct simple structured_data from metadata + title
        structured_data = metadata.copy()
        structured_data["title"] = result[6]

        # Optionally: Query fact_items to populate lists if needed for full fidelity
        # This is a "lazy" reconstruction

        return StoredEntity(
            entity_id=result[0],
            source_type=result[1],
            source_url=result[2],
            raw_content=result[3],
            structured_data=structured_data,
            metadata=metadata,
            created_at=result[5],
        )

    async def query_entities(
        self,
        source_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[StoredEntity]:
        """Query entities (documents)."""
        if source_type:
            query = """
                SELECT doc_id, source_type, url, full_text_blob,
                       metadata, created_at, title
                FROM dim_documents
                WHERE source_type = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            params = [source_type, limit, offset]
        else:
            query = """
                SELECT doc_id, source_type, url, full_text_blob,
                       metadata, created_at, title
                FROM dim_documents
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            params = [limit, offset]

        results = self.conn.execute(query, params).fetchall()

        entities = []
        for row in results:
            metadata = json.loads(row[4])
            structured_data = metadata.copy()
            structured_data["title"] = row[6]

            entities.append(StoredEntity(
                entity_id=row[0],
                source_type=row[1],
                source_url=row[2],
                raw_content=row[3],
                structured_data=structured_data,
                metadata=metadata,
                created_at=row[5],
            ))

        return entities

    async def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity and its facts."""
        # Cascade delete logic
        # First delete facts
        self.conn.execute("DELETE FROM fact_items WHERE doc_id = ?", [entity_id])
        # Then delete doc
        result = self.conn.execute("DELETE FROM dim_documents WHERE doc_id = ?", [entity_id])
        return result.fetchone()[0] > 0

    async def count_entities(self, source_type: str | None = None) -> int:
        """Count documents."""
        if source_type:
            result = self.conn.execute(
                "SELECT COUNT(*) FROM dim_documents WHERE source_type = ?",
                [source_type],
            )
        else:
            result = self.conn.execute("SELECT COUNT(*) FROM dim_documents")

        return result.fetchone()[0]

    async def retrieve_context(
        self,
        query_vector: list[float],
        filters: dict[str, Any] | None = None,
        limit: int = 5
    ) -> list[dict[str, Any]]:
        """Retrieve context using hybrid search (vector + SQL).

        This is the key 'Unlock' method described in the research.
        """
        # Basic cosine similarity using list functions if VSS not installed
        # Note: array_cosine_similarity might need VSS or recent DuckDB
        # Fallback to exact match or simple SQL for now if vector not ready.

        # Construct the query dynamically
        sql = """
        SELECT
            item.content_text,
            item.item_type,
            item.properties,
            doc.title,
            doc.url,
            item.location_pointer
        FROM fact_items item
        JOIN dim_documents doc ON item.doc_id = doc.doc_id
        WHERE 1=1
        """

        params = []

        # Apply filters on properties JSON
        if filters:
            for k, v in filters.items():
                # DuckDB JSON extraction: json_extract_string(json, '$.key')
                # This assumes filters are simple equality checks on string values
                sql += f" AND json_extract_string(item.properties, '$.{k}') = ?"
                params.append(v)

        # Vector search part
        # Since we don't have real embeddings in this POC, we'll skip the ORDER BY vector similarity
        # and just return the top filtered results.
        # In a real implementation, this would use array_cosine_similarity(item.embedding, ?::FLOAT[])

        sql += " LIMIT ?"
        params.append(limit)

        results = self.conn.execute(sql, params).fetchall()

        return [
            {
                "content": r[0],
                "type": r[1],
                "properties": json.loads(r[2]),
                "source_title": r[3],
                "source_url": r[4],
                "location": r[5]
            }
            for r in results
        ]

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()
