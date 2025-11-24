# structure-it

A research sandbox for exploring structured data extraction and modeling in LLM-driven data pipelines.

## Overview

**structure-it** is a research sandbox for exploring structured data extraction and LLM-driven data pipelines. Extract structured data from any unstructured source using multimodal LLMs (Gemini), experiment with data modeling approaches, and build reusable components for extraction and generation.

This is an exploratory research project focused on:
- Structured data extraction from text, images, PDFs, and web content
- Domain-specific schemas (academic papers, articles, code docs, meeting notes, policies, etc.)
- Data modeling approaches for LLM context management
- Reusable generators for creating synthetic test data
- Comparing different storage patterns (JSON, DuckDB, future: star schema/graph)
- **New:** "Structure Studio" UI for visual data exploration and analysis.

## Quick Start

### Installation

```bash
# Create virtual environment
uv venv
source .venv/bin/activate  # or .venv/Scripts/activate on Windows

# Install package
uv pip install -e ".[dev]"

# Optional: Install with UI/Server support
uv pip install -e ".[server,dev]"

# Optional: Install with genai-processors support
uv pip install -e ".[processors,dev]"
```

### Running the UI

To start both the backend API and the React frontend with a single command:

```bash
./start.sh
```

This will launch:
*   **Backend API**: http://localhost:8000
*   **Structure Studio**: http://localhost:5173

### Configuration

All settings are centralized in environment variables:

```bash
# Required: Google API key
export GOOGLE_API_KEY="your-api-key-here"
# Get your key from: https://aistudio.google.com/app/apikey

# Optional: Model configuration (default: gemini-2.5-flash)
export STRUCTURE_IT_MODEL="gemini-2.5-flash"

# Optional: Generation temperature (default: 0.8)
export STRUCTURE_IT_TEMPERATURE="0.8"
```

No hardcoded model names anywhere! Everything uses these config values.

### Run Examples

```bash
# Extract structured recipe data from text
uv run python examples/extract_recipe.py

# Extract web article from URL (with storage)
uv run python examples/extract_web_article.py https://python.org/about/

# Extract academic paper from PDF/URL or generated ArXiv papers
uv run python examples/extract_academic_paper.py paper.pdf

# Extract policy requirements (example domain-specific extractor)
uv run python examples/extract_policy_requirements.py \
  data/sample_policies/full_dataset/FIN-001_expense_reimbursement.md \
  --metadata data/sample_policies/full_dataset/metadata.json
```

## Example Usage

### Basic Extraction

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

### Domain-Specific Extraction

```python
import asyncio
from structure_it.extractors import PolicyRequirementsExtractor

async def main():
    # Example: Policy requirements (one domain among many)
    extractor = PolicyRequirementsExtractor()

    requirements = await extractor.extract(
        pdf_path="policy.pdf",  # Supports both PDF and markdown
        policy_metadata={
            "policy_id": "FIN-001",
            "policy_title": "Expense Reimbursement Policy",
            "policy_type": "Financial",
        }
    )

    print(f"Extracted {requirements.total_requirements} requirements")

asyncio.run(main())
```

See [docs/policy_requirements_guide.md](docs/policy_requirements_guide.md) for policy extraction details.

## Features

### Core Components

**Extractors** - Extract structured data from unstructured content
- `GeminiExtractor`: General-purpose extraction with any Pydantic schema
- `PolicyRequirementsExtractor`: Example domain-specific extractor
- Easy to create custom extractors for any domain

**Generators** - Create synthetic content for testing
- `BaseGenerator`: Reusable LLM-powered content generation
- `PolicyGenerator`: Policy documents (5 domains: Financial, IT, HR, Legal, Compliance)
- `ArxivGenerator`: AI/ML research papers (6 focus areas)
- `CivicDocumentGenerator`: Local government documents (agendas, minutes, proposals)
- Extensible pattern - easy to add more domains

**Schemas** - 6 domain-specific Pydantic models
- Academic Papers, Web Articles, Code Documentation
- Meeting Notes, Media Transcripts, Policy Requirements
- BaseSchema with validation and serialization
- Easy to add new domains

**Local Govt Citizen Data** - Robust data collection
- **Transparent and Respectful**: Built-in `AutoThrottle`, `SafeSession` for downloads, and User-Agent identification
- **CDC**: Change Data Capture pipeline to only process new/changed documents (saves LLM costs, is respectful to the upstream systems)

**Storage** - Flexible persistence backends
- JSON Storage: Simple file-based (great for prototyping)
- DuckDB Storage: Analytical queries with JSON columns
- Star Schema Storage: Dimensional Context Model for granular LLM retrieval
- SHA256-based IDs: Deterministic, idempotent

**Config** - Centralized configuration (`config.py`)
- Model defaults via `STRUCTURE_IT_MODEL` env var
- Temperature, storage paths, all configurable
- No hardcoded values scattered through code

**Server** - FastAPI application (`server/main.py`)
- Exposes the core extraction library via a REST API
- Serves the React-based user interface
- Provides a simple way to interact with the core library without writing Python code

### UI (Structure Studio)

**Single Pane of Glass** - A unified workspace for data operations
- **Citizen Explorer**: Visualize civic data, timelines, and topic trends.
- **Compliance Monitor**: Extract requirements from policies and visualize relationships as a knowledge graph.
- **Data Sources**: Ingest documents via drag-and-drop with auto-detection.
- **Atomic Inspector**: Deep-dive into raw JSON data and vector embeddings for any entity.

#### Architecture

The `structure-it` sandbox is composed of a core extraction library, a FastAPI server, and a React-based Single Pane of Glass UI ("Structure Studio").

```
+----------------------------------------------------------------+
|     React UI (ui/) - "Structure Studio"                        |
|     - Single Pane of Glass (App Shell)                         |
|     - Apps: CitizenExplorer, ComplianceMonitor, DataSources    |
+----------------------------------------------------------------+
      | (HTTP API)
+----------------------------------------------------------------+
|     FastAPI Server (server/)                                   |
|     - Serves the UI                                            |
|     - Provides an API for the core library                     |
+----------------------------------------------------------------+
      | (Python API)
+----------------------------------------------------------------+
|     Core Library (src/structure_it/)                           |
|                                                                |
|     +-----------------+  +-----------------+  +--------------+ |
|     |   Extractors    |  |    Generators   |  |   Schemas    | |
|     | (GeminiExtractor) |  | (PolicyGenerator) |  | (Pydantic)   | |
|     +-----------------+  +-----------------+  +--------------+ |
|           |                      |                   |         |
|     +------------------------------------------------------+   |
|     |   Storage (DuckDB, JSON)                             |   |
|     +------------------------------------------------------+   |
|           |                                                |   |
|     +------------------------------------------------------+   |
|     |   Google Gemini API                                  |   |
|     +------------------------------------------------------+   |
+----------------------------------------------------------------+
```
