"""Example: Extract structured data from web articles using markitdown.

This example demonstrates:
1. Converting web page HTML to markdown using markitdown
2. Extracting structured data with Gemini
3. Storing results in both JSON and DuckDB

Usage:
    uv run python examples/extract_web_article.py <url>

Example:
    uv run python examples/extract_web_article.py https://example.com/article
"""

import asyncio
import os
import sys
from urllib.parse import urlparse

from markitdown import MarkItDown

from structure_it.extractors import GeminiExtractor
from structure_it.schemas.articles import WebArticle
from structure_it.storage import DuckDBStorage, JSONStorage
from structure_it.utils import generate_entity_id


async def fetch_and_convert(url: str) -> str:
    """Fetch web page and convert to markdown.

    Args:
        url: URL of the web page.

    Returns:
        Markdown content of the page.
    """
    print(f"Fetching: {url}")
    md = MarkItDown()
    result = md.convert(url)
    return result.text_content


async def main() -> None:
    """Run the web article extraction example."""
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set")
        print("Please set your Google API key:")
        print("  export GOOGLE_API_KEY='your-api-key-here'")
        return

    # Get URL from command line
    if len(sys.argv) < 2:
        print("Usage: uv run python examples/extract_web_article.py <url>")
        print("\nExample URLs to try:")
        print("  - https://python.org/about/")
        print("  - https://github.com/anthropics/anthropic-sdk-python")
        print("  - Any blog post or article URL")
        return

    url = sys.argv[1]

    print("=" * 80)
    print("Web Article Extraction Example")
    print("=" * 80)
    print()

    # Step 1: Fetch and convert to markdown
    try:
        markdown_content = await fetch_and_convert(url)
        print(f"✓ Converted to markdown ({len(markdown_content)} characters)")
        print()
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return

    # Step 2: Extract structured data
    print("Extracting structured article data...")
    extractor = GeminiExtractor(
        schema=WebArticle,
        model_name="gemini-2.0-flash-exp",
    )

    try:
        article = await extractor.extract(
            content=markdown_content,
            prompt=(
                "Extract structured information from this web article. "
                "Include the title, author, main content, key points, "
                "technologies/tools mentioned, and any other relevant metadata. "
                "Be thorough but concise."
            ),
        )
        print("✓ Extraction complete")
        print()
    except Exception as e:
        print(f"Error during extraction: {e}")
        return

    # Step 3: Display results
    print("Extracted Article:")
    print("-" * 80)
    print(f"Title: {article.title}")
    if article.author:
        print(f"Author: {article.author.name}")
    if article.published_date:
        print(f"Published: {article.published_date}")
    if article.summary:
        print(f"\nSummary: {article.summary}")
    if article.key_points:
        print(f"\nKey Points:")
        for point in article.key_points[:5]:  # Show first 5
            print(f"  - {point}")
    if article.technologies_mentioned:
        print(f"\nTechnologies: {', '.join(article.technologies_mentioned)}")
    if article.tags:
        print(f"Tags: {', '.join(article.tags)}")
    print()

    # Step 4: Store in both JSON and DuckDB
    entity_id = generate_entity_id(url, "web_article")

    print("Storing results...")
    print()

    # Store in JSON
    json_storage = JSONStorage()
    await json_storage.store_entity(
        entity_id=entity_id,
        source_type="web_article",
        source_url=url,
        raw_content=markdown_content,
        structured_data=article.to_dict(),
        metadata={
            "extractor": "GeminiExtractor",
            "model": "gemini-2.0-flash-exp",
            "markdown_length": len(markdown_content),
        },
    )
    print(f"✓ Stored in JSON: ./data/entities/{entity_id[:2]}/{entity_id}.json")

    # Store in DuckDB
    duckdb_storage = DuckDBStorage()
    await duckdb_storage.store_entity(
        entity_id=entity_id,
        source_type="web_article",
        source_url=url,
        raw_content=markdown_content,
        structured_data=article.to_dict(),
        metadata={
            "extractor": "GeminiExtractor",
            "model": "gemini-2.0-flash-exp",
            "markdown_length": len(markdown_content),
        },
    )
    print(f"✓ Stored in DuckDB: ./data/structure_it.duckdb")
    print()

    # Step 5: Verify storage
    print("Verifying storage...")
    json_count = await json_storage.count_entities(source_type="web_article")
    duckdb_count = await duckdb_storage.count_entities(source_type="web_article")
    print(f"  JSON: {json_count} web articles")
    print(f"  DuckDB: {duckdb_count} web articles")
    print()

    print("=" * 80)
    print("Success! Article extracted and stored.")
    print("=" * 80)
    print()
    print("Full JSON output:")
    print(article.to_json())


if __name__ == "__main__":
    asyncio.run(main())
