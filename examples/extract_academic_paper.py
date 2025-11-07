"""Example: Extract structured data from academic papers.

This example demonstrates extracting paper metadata, abstract, sections,
and citations from academic papers (text, markdown, or PDF via markitdown).

Usage:
    uv run python examples/extract_academic_paper.py <file_or_url>
"""

import asyncio
import os
import sys
from pathlib import Path

from markitdown import MarkItDown

from structure_it.extractors import GeminiExtractor
from structure_it.schemas.academic import AcademicPaper
from structure_it.storage import JSONStorage
from structure_it.utils import generate_entity_id


async def load_paper(source: str) -> tuple[str, str]:
    """Load paper content from file or URL.

    Args:
        source: File path or URL.

    Returns:
        Tuple of (content, source_url).
    """
    md = MarkItDown()

    if source.startswith(("http://", "https://")):
        print(f"Fetching from URL: {source}")
        result = md.convert(source)
        return result.text_content, source
    else:
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {source}")

        print(f"Loading from file: {source}")
        if path.suffix.lower() == ".pdf":
            result = md.convert(str(path))
            return result.text_content, f"file://{path.absolute()}"
        else:
            # Plain text or markdown
            return path.read_text(), f"file://{path.absolute()}"


async def main() -> None:
    """Run academic paper extraction example."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set")
        return

    if len(sys.argv) < 2:
        print("Usage: uv run python examples/extract_academic_paper.py <file_or_url>")
        print("\nExamples:")
        print("  uv run python examples/extract_academic_paper.py paper.pdf")
        print("  uv run python examples/extract_academic_paper.py https://arxiv.org/abs/2301.00001")
        return

    source = sys.argv[1]

    print("=" * 80)
    print("Academic Paper Extraction")
    print("=" * 80)
    print()

    # Load paper
    try:
        content, source_url = await load_paper(source)
        print(f"✓ Loaded ({len(content)} characters)")
        print()
    except Exception as e:
        print(f"Error loading paper: {e}")
        return

    # Extract
    print("Extracting structured data...")
    extractor = GeminiExtractor(schema=AcademicPaper, model_name="gemini-2.0-flash-exp")

    try:
        paper = await extractor.extract(
            content=content,
            prompt=(
                "Extract structured information from this academic paper. "
                "Include title, authors with affiliations, abstract, key sections, "
                "methodology, results, findings, and citations. "
                "Be thorough and accurate."
            ),
        )
        print("✓ Extraction complete")
        print()
    except Exception as e:
        print(f"Error during extraction: {e}")
        return

    # Display
    print("Extracted Paper:")
    print("-" * 80)
    print(f"Title: {paper.title}")
    print(f"Authors: {', '.join(a.name for a in paper.authors)}")
    if paper.publication_year:
        print(f"Year: {paper.publication_year}")
    if paper.venue:
        print(f"Venue: {paper.venue}")
    print(f"\nAbstract:\n{paper.abstract[:300]}...")
    if paper.key_findings:
        print(f"\nKey Findings:")
        for finding in paper.key_findings[:3]:
            print(f"  - {finding}")
    if paper.citations:
        print(f"\nCitations: {len(paper.citations)}")
    print()

    # Store
    entity_id = generate_entity_id(source_url, "academic_paper")
    storage = JSONStorage()

    await storage.store_entity(
        entity_id=entity_id,
        source_type="academic_paper",
        source_url=source_url,
        raw_content=content,
        structured_data=paper.to_dict(),
        metadata={"model": "gemini-2.0-flash-exp"},
    )

    print(f"✓ Stored in JSON storage")
    print()
    print("=" * 80)
    print("Success!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
