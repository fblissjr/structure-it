"""Transform script for ELT architecture (Raw -> Staged).

Reads from data/raw/ (Bronze) and outputs to data/staged/ (Silver).

Transformations:
1. Convert original files to markdown (MarkItDown)
2. Extract structured data via Gemini
3. Save as JSON ready for DuckDB loading

Usage:
    uv run python -m structure_it.etl.transform
    uv run python -m structure_it.etl.transform --source-type civic_meeting
    uv run python -m structure_it.etl.transform --entity-id abc123
    uv run python -m structure_it.etl.transform --force  # Re-transform even if staged exists
"""

import argparse
import asyncio
import json
from datetime import datetime
from pathlib import Path

from markitdown import MarkItDown

from structure_it.extractors import GeminiExtractor
from structure_it.schemas.civic import (
    BuildingPermit,
    CivicBid,
    CivicFinancialReport,
    CivicMeeting,
    CivicServiceRequest,
)
from structure_it.utils.hashing import generate_id


# Schema mapping by source type
EXTRACTORS = {
    "civic_meeting": (CivicMeeting, "Extract meeting data from this document."),
    "building_permit": (BuildingPermit, "Extract building permit data from this document."),
    "civic_bid": (CivicBid, "Extract bid/RFP data from this document."),
    "civic_service_request": (CivicServiceRequest, "Extract service request data."),
    "civic_financial_report": (CivicFinancialReport, "Extract financial report data."),
}


async def transform_item(
    raw_dir: Path,
    staged_dir: Path,
    md_converter: MarkItDown,
    force: bool = False,
) -> dict | None:
    """Transform a single raw item to staged format.

    Args:
        raw_dir: Path to raw item folder (e.g., data/raw/civic_meeting/abc123/)
        staged_dir: Path to staged output folder (e.g., data/staged/civic_meeting/)
        md_converter: MarkItDown instance
        force: Re-transform even if staged file exists

    Returns:
        Staged record dict, or None if skipped/failed
    """
    # Read source metadata
    source_path = raw_dir / "source.json"
    if not source_path.exists():
        print(f"  [SKIP] No source.json in {raw_dir}")
        return None

    with open(source_path) as f:
        source = json.load(f)

    entity_id = source["entity_id"]
    source_type = source["source_type"]

    # Check if already staged
    staged_path = staged_dir / f"{entity_id}.json"
    if staged_path.exists() and not force:
        print(f"  [SKIP] Already staged: {entity_id}")
        return None

    print(f"  [TRANSFORM] {entity_id} ({source_type})")

    # Find original file
    original_file = None
    for ext in [".pdf", ".html", ".htm"]:
        candidate = raw_dir / f"original{ext}"
        if candidate.exists():
            original_file = candidate
            break

    if not original_file:
        print(f"  [ERROR] No original file found in {raw_dir}")
        return None

    # 1. Convert to markdown
    print(f"    Converting {original_file.name} to markdown...")
    try:
        result = await asyncio.to_thread(md_converter.convert, str(original_file))
        content_md = result.text_content
    except Exception as e:
        print(f"    [ERROR] Markdown conversion failed: {e}")
        return None

    content_hash = generate_id(content_md)

    # 2. Extract with Gemini
    print(f"    Extracting with Gemini...")
    schema_class, base_prompt = EXTRACTORS.get(source_type, (CivicMeeting, "Extract data."))

    extractor = GeminiExtractor(schema=schema_class)

    # Build contextual prompt
    prompt_parts = [base_prompt]
    if source.get("title"):
        prompt_parts.append(f"Title: {source['title']}")
    if source.get("committee_name"):
        prompt_parts.append(f"Committee: {source['committee_name']}")
    if source.get("meeting_date"):
        prompt_parts.append(f"Date: {source['meeting_date']}")

    prompt = " ".join(prompt_parts)

    try:
        extracted = await extractor.extract(content=content_md, prompt=prompt)
        extracted_data = extracted.to_dict()

        # Augment with source metadata
        extracted_data["source_url"] = source.get("url")
        if hasattr(extracted, "document_type") and source.get("asset_type"):
            extracted_data["document_type"] = source["asset_type"]
        if hasattr(extracted, "government_body") and source.get("committee_name"):
            extracted_data["government_body"] = source["committee_name"]

    except Exception as e:
        print(f"    [ERROR] Gemini extraction failed: {e}")
        return None

    # 3. Build staged record (ready for DuckDB)
    staged_record = {
        # Identity
        "entity_id": entity_id,
        "source_type": source_type,
        "url": source.get("url"),
        # Content
        "content_md": content_md,
        "content_hash": content_hash,
        # Extracted structured data
        "extracted": extracted_data,
        # Source metadata passthrough
        "source_metadata": source,
        # Timestamps
        "transformed_at": datetime.now().isoformat(),
    }

    # 4. Save to staged
    staged_dir.mkdir(parents=True, exist_ok=True)
    staged_path.write_text(json.dumps(staged_record, indent=2, default=str), encoding="utf-8")
    print(f"    [OK] Staged -> {staged_path}")

    return staged_record


async def transform_all(
    raw_base: Path,
    staged_base: Path,
    source_type: str | None = None,
    entity_id: str | None = None,
    force: bool = False,
) -> tuple[int, int, int]:
    """Transform all raw items to staged format.

    Returns:
        Tuple of (transformed, skipped, failed) counts
    """
    md = MarkItDown()
    transformed = 0
    skipped = 0
    failed = 0

    # Find items to transform
    if entity_id and source_type:
        # Single item
        raw_dirs = [raw_base / source_type / entity_id]
    elif source_type:
        # All items of a source type
        source_dir = raw_base / source_type
        raw_dirs = [d for d in source_dir.iterdir() if d.is_dir()] if source_dir.exists() else []
    else:
        # All items across all source types
        raw_dirs = []
        for source_dir in raw_base.iterdir():
            if source_dir.is_dir() and not source_dir.name.startswith("."):
                raw_dirs.extend(d for d in source_dir.iterdir() if d.is_dir())

    print(f"Found {len(raw_dirs)} raw items to process")

    for raw_dir in raw_dirs:
        # Determine staged output dir
        parts = raw_dir.relative_to(raw_base).parts
        if len(parts) >= 1:
            item_source_type = parts[0]
            staged_dir = staged_base / item_source_type

            result = await transform_item(raw_dir, staged_dir, md, force)
            if result:
                transformed += 1
            elif result is None:
                # Check if it was skipped or failed
                source_path = raw_dir / "source.json"
                staged_path = staged_dir / f"{raw_dir.name}.json"
                if staged_path.exists() and not force:
                    skipped += 1
                else:
                    failed += 1

    return transformed, skipped, failed


def main():
    parser = argparse.ArgumentParser(description="Transform raw data to staged format")
    parser.add_argument("--raw-dir", default="./data/raw", help="Raw data directory")
    parser.add_argument("--staged-dir", default="./data/staged", help="Staged output directory")
    parser.add_argument("--source-type", help="Filter by source type")
    parser.add_argument("--entity-id", help="Transform specific entity")
    parser.add_argument("--force", action="store_true", help="Re-transform even if staged exists")

    args = parser.parse_args()

    print("=" * 60)
    print("TRANSFORM: Raw -> Staged")
    print("=" * 60)
    print(f"Raw dir: {args.raw_dir}")
    print(f"Staged dir: {args.staged_dir}")
    print()

    transformed, skipped, failed = asyncio.run(
        transform_all(
            Path(args.raw_dir),
            Path(args.staged_dir),
            args.source_type,
            args.entity_id,
            args.force,
        )
    )

    print()
    print("=" * 60)
    print(f"Transformed: {transformed}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")
    print("=" * 60)


if __name__ == "__main__":
    main()
