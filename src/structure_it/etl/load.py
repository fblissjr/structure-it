"""Load script for ELT architecture (Staged -> DuckDB).

Reads from data/staged/ (Silver) and loads to DuckDB (Gold).

Features:
- CDC: Only loads new/changed records (based on content_hash)
- Idempotent: Safe to re-run
- Audit trail: Logs all changes

Usage:
    uv run python -m structure_it.etl.load
    uv run python -m structure_it.etl.load --source-type civic_meeting
    uv run python -m structure_it.etl.load --entity-id abc123
    uv run python -m structure_it.etl.load --force  # Reload even if unchanged
"""

import argparse
import asyncio
import json
from datetime import datetime
from pathlib import Path

from structure_it.storage.star_schema_storage import StarSchemaStorage


async def load_item(
    staged_path: Path,
    storage: StarSchemaStorage,
    force: bool = False,
) -> tuple[str, str]:
    """Load a single staged item to DuckDB.

    Args:
        staged_path: Path to staged JSON file
        storage: StarSchemaStorage instance
        force: Load even if unchanged

    Returns:
        Tuple of (entity_id, status) where status is 'created', 'updated', 'unchanged', or 'error'
    """
    try:
        with open(staged_path) as f:
            record = json.load(f)

        entity_id = record["entity_id"]
        source_type = record["source_type"]
        content_hash = record["content_hash"]
        url = record.get("url", "")
        content_md = record.get("content_md", "")
        extracted = record.get("extracted", {})
        source_metadata = record.get("source_metadata", {})

        # CDC check
        is_new, has_changed = storage.check_document_status(entity_id, content_hash)

        if not force and not is_new and not has_changed:
            return entity_id, "unchanged"

        # Store entity
        await storage.store_entity(
            entity_id=entity_id,
            source_type=source_type,
            source_url=url,
            raw_content=content_md,
            structured_data=extracted,
            metadata=source_metadata,
        )

        status = "created" if is_new else "updated"
        return entity_id, status

    except Exception as e:
        print(f"    [ERROR] {staged_path.name}: {e}")
        return staged_path.stem, "error"


async def load_all(
    staged_base: Path,
    db_path: Path,
    source_type: str | None = None,
    entity_id: str | None = None,
    force: bool = False,
) -> dict[str, int]:
    """Load all staged items to DuckDB.

    Returns:
        Dict of status counts: {'created': N, 'updated': N, 'unchanged': N, 'error': N}
    """
    storage = StarSchemaStorage(db_path=db_path)
    counts = {"created": 0, "updated": 0, "unchanged": 0, "error": 0}

    # Find staged files to load
    if entity_id and source_type:
        staged_files = [staged_base / source_type / f"{entity_id}.json"]
    elif source_type:
        source_dir = staged_base / source_type
        staged_files = list(source_dir.glob("*.json")) if source_dir.exists() else []
    else:
        staged_files = list(staged_base.glob("**/*.json"))

    # Filter to only existing files
    staged_files = [f for f in staged_files if f.exists()]

    print(f"Found {len(staged_files)} staged files to load")

    for staged_path in staged_files:
        entity_id, status = await load_item(staged_path, storage, force)
        counts[status] += 1

        if status in ("created", "updated"):
            print(f"  [{status.upper()}] {entity_id}")
        elif status == "error":
            print(f"  [ERROR] {entity_id}")
        # Skip logging 'unchanged' to reduce noise

    storage.close()
    return counts


def main():
    parser = argparse.ArgumentParser(description="Load staged data to DuckDB")
    parser.add_argument("--staged-dir", default="./data/staged", help="Staged data directory")
    parser.add_argument("--db-path", default="./data/structure_it.duckdb", help="DuckDB path")
    parser.add_argument("--source-type", help="Filter by source type")
    parser.add_argument("--entity-id", help="Load specific entity")
    parser.add_argument("--force", action="store_true", help="Reload even if unchanged")

    args = parser.parse_args()

    print("=" * 60)
    print("LOAD: Staged -> DuckDB")
    print("=" * 60)
    print(f"Staged dir: {args.staged_dir}")
    print(f"DB path: {args.db_path}")
    print()

    counts = asyncio.run(
        load_all(
            Path(args.staged_dir),
            Path(args.db_path),
            args.source_type,
            args.entity_id,
            args.force,
        )
    )

    print()
    print("=" * 60)
    print(f"Created: {counts['created']}")
    print(f"Updated: {counts['updated']}")
    print(f"Unchanged: {counts['unchanged']}")
    print(f"Errors: {counts['error']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
