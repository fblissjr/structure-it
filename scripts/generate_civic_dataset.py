"""Generate synthetic civic/government meeting documents dataset.

Creates a dataset of realistic local government documents:
- Meeting Agendas: 3 documents (simple, medium, complex)
- Meeting Minutes: 2 documents (simple, medium)
- Proposals: 2 documents (medium, complex)
- Resolutions: 1 document (simple)

Usage:
    uv run python scripts/generate_civic_dataset.py [--count N]
"""

import argparse
import asyncio
import csv
import json
import os
from datetime import datetime
from pathlib import Path

from structure_it.generators import CivicDocumentGenerator


async def generate_civic_dataset(count: int | None = None) -> None:
    """Generate civic documents dataset.

    Args:
        count: Optional number of documents to generate (default: all 8).
    """
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set")
        print("Please set your Google API key:")
        print("  export GOOGLE_API_KEY='your-api-key-here'")
        return

    print()
    print("=" * 80)
    print("Generating Civic/Government Documents Dataset")
    print("=" * 80)
    print()

    # Define all documents to generate
    all_documents = [
        # Agendas (3)
        {
            "doc_id": "TWP-2024-001",
            "doc_type": "agenda",
            "municipality": "Springfield Township",
            "gov_type": "township",
            "meeting_date": "2024-01-15",
            "complexity": "simple",
            "filename": "TWP-2024-001_agenda_simple.md",
        },
        {
            "doc_id": "VIL-2024-002",
            "doc_type": "agenda",
            "municipality": "Riverside Village",
            "gov_type": "village",
            "meeting_date": "2024-02-20",
            "complexity": "medium",
            "filename": "VIL-2024-002_agenda_medium.md",
        },
        {
            "doc_id": "CTY-2024-003",
            "doc_type": "agenda",
            "municipality": "Madison County",
            "gov_type": "county",
            "meeting_date": "2024-03-12",
            "complexity": "complex",
            "filename": "CTY-2024-003_agenda_complex.md",
        },
        # Minutes (2)
        {
            "doc_id": "TWP-2024-004",
            "doc_type": "minutes",
            "municipality": "Springfield Township",
            "gov_type": "township",
            "meeting_date": "2024-01-15",
            "complexity": "simple",
            "filename": "TWP-2024-004_minutes_simple.md",
        },
        {
            "doc_id": "VIL-2024-005",
            "doc_type": "minutes",
            "municipality": "Riverside Village",
            "gov_type": "village",
            "meeting_date": "2024-02-20",
            "complexity": "medium",
            "filename": "VIL-2024-005_minutes_medium.md",
        },
        # Proposals (2)
        {
            "doc_id": "TWP-PROP-2024-001",
            "doc_type": "proposal",
            "municipality": "Springfield Township",
            "gov_type": "township",
            "meeting_date": "2024-01-10",
            "complexity": "medium",
            "filename": "TWP-PROP-2024-001_infrastructure_proposal.md",
        },
        {
            "doc_id": "VIL-PROP-2024-002",
            "doc_type": "proposal",
            "municipality": "Riverside Village",
            "gov_type": "village",
            "meeting_date": "2024-02-15",
            "complexity": "complex",
            "filename": "VIL-PROP-2024-002_development_proposal.md",
        },
        # Resolutions (1)
        {
            "doc_id": "RES-2024-001",
            "doc_type": "resolution",
            "municipality": "Springfield Township",
            "gov_type": "township",
            "meeting_date": "2024-01-15",
            "complexity": "simple",
            "filename": "RES-2024-001_budget_resolution.md",
        },
    ]

    # Limit if count specified
    if count:
        documents = all_documents[:count]
    else:
        documents = all_documents

    print(f"Generating {len(documents)} civic documents...")
    print()

    # Create output directory
    output_dir = Path("data/sample_civic")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize generator
    generator = CivicDocumentGenerator()

    # Generate documents
    metadata_list = []
    for idx, doc in enumerate(documents, 1):
        print(f"[{idx}/{len(documents)}] {doc['doc_type'].title()}: {doc['municipality']}")
        print(f"            ID: {doc['doc_id']}")
        print(f"            Date: {doc['meeting_date']}")
        print(f"            Complexity: {doc['complexity']}")

        try:
            # Generate document (vary temperature for diversity)
            temp = 0.7 + (idx % 3) * 0.1  # 0.7, 0.8, 0.9
            content = await generator.generate_meeting_document(
                doc_id=doc["doc_id"],
                doc_type=doc["doc_type"],
                municipality=doc["municipality"],
                gov_type=doc["gov_type"],
                meeting_date=doc["meeting_date"],
                complexity=doc["complexity"],
                temperature=temp,
            )

            # Save markdown
            md_path = output_dir / doc["filename"]
            generator.save_as_markdown(content, md_path)

            print(f"            ✓ Saved: {md_path.name}")
            print(f"            Length: {len(content):,} characters")
            print()

            # Build metadata
            metadata = {
                "doc_id": doc["doc_id"],
                "doc_type": doc["doc_type"],
                "municipality": doc["municipality"],
                "gov_type": doc["gov_type"],
                "meeting_date": doc["meeting_date"],
                "complexity": doc["complexity"],
                "filename": doc["filename"],
                "character_count": len(content),
                "generated_at": datetime.utcnow().isoformat(),
                "model": generator.model_name,
                "temperature": temp,
            }
            metadata_list.append(metadata)

        except Exception as e:
            print(f"            ✗ Error: {e}")
            import traceback

            traceback.print_exc()
            print()
            continue

    # Save metadata as JSON
    metadata_json_path = output_dir / "metadata.json"
    with open(metadata_json_path, "w") as f:
        json.dump(metadata_list, f, indent=2)

    # Save metadata as CSV
    metadata_csv_path = output_dir / "metadata.csv"
    if metadata_list:
        with open(metadata_csv_path, "w", newline="") as f:
            fieldnames = metadata_list[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(metadata_list)

    # Generate summary statistics
    print("=" * 80)
    print("Civic Documents Dataset Generation Complete")
    print("=" * 80)
    print()
    print(f"Location: {output_dir}")
    print(f"Total Documents: {len(metadata_list)}")
    print()

    # Breakdown by type
    by_type = {}
    by_complexity = {}
    for meta in metadata_list:
        doc_type = meta["doc_type"]
        complexity = meta["complexity"]
        by_type[doc_type] = by_type.get(doc_type, 0) + 1
        by_complexity[complexity] = by_complexity.get(complexity, 0) + 1

    print("By Document Type:")
    for dtype, count in sorted(by_type.items()):
        print(f"  {dtype.title()}: {count}")
    print()

    print("By Complexity:")
    for complexity, count in sorted(by_complexity.items()):
        print(f"  {complexity}: {count}")
    print()

    print(f"Metadata saved:")
    print(f"  JSON: {metadata_json_path}")
    print(f"  CSV: {metadata_csv_path}")
    print()

    print("Next Steps:")
    print("1. Review the generated documents")
    print("2. Test extraction with meeting schemas")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate civic/government documents dataset"
    )
    parser.add_argument(
        "--count",
        type=int,
        help="Number of documents to generate (default: all 8)",
    )
    args = parser.parse_args()

    asyncio.run(generate_civic_dataset(count=args.count))
