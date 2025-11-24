"""Example of extracting structured documentation from a code file."""

import asyncio
from pathlib import Path
import sys

from structure_it.extractors import CodeDocsExtractor


async def extract_code_documentation(file_path: str) -> None:
    """Extract and print structured code documentation."""
    extractor = CodeDocsExtractor()

    try:
        docs = await extractor.extract(file_path=Path(file_path))
        print(f"--- Extracted Documentation for {file_path} ---")
        print(docs.to_json())
    except Exception as e:
        print(f"Error extracting documentation from {file_path}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python examples/extract_code_docs.py <path_to_code_file>")
        print("Example: uv run python examples/extract_code_docs.py src/structure_it/utils/hashing.py")
        sys.exit(1)

    target_file = sys.argv[1]
    asyncio.run(extract_code_documentation(target_file))
