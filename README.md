# structure-it

A research sandbox for exploring structured data extraction and modeling in LLM-driven data pipelines.

## Overview

**structure-it** provides tools for extracting structured data from unstructured sources using multimodal LLMs (starting with Google Gemini) and experimenting with different data modeling approaches optimized for LLM context and reuse.

This is an exploratory research project focused on:
- Structured data extraction from text, images, and documents
- Data modeling approaches for LLM context management
- Multimodal data pipeline experimentation
- Comparing different modeling patterns (dimensional, graph, hybrid)

## Quick Start

### Installation

```bash
# Create virtual environment
uv venv
source .venv/bin/activate  # or .venv/Scripts/activate on Windows

# Install package
uv pip install -e ".[dev]"

# Optional: Install with genai-processors support
uv pip install -e ".[processors,dev]"
```

### Setup API Key

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Google API key
# Get your key from: https://aistudio.google.com/app/apikey
```

### Run Example

```bash
# Extract structured recipe data from text
uv run python examples/extract_recipe.py
```

## Example Usage

```python
import asyncio
from structure_it.extractors import GeminiExtractor
from structure_it.schemas import BaseSchema


class Recipe(BaseSchema):
    name: str
    ingredients: list[str]
    instructions: list[str]


async def main():
    extractor = GeminiExtractor(schema=Recipe)

    recipe = await extractor.extract(
        content="Your recipe text here...",
        prompt="Extract recipe information from the text."
    )

    print(recipe.to_json())


asyncio.run(main())
```

## Project Status

- Minimal architecture with direct Gemini API integration
- Pydantic schemas for structured outputs
- Basic extraction capabilities

## License

Apache 2.0 - See [LICENSE](LICENSE) for details.
