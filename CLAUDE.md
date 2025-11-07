# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**structure-it** is a research sandbox for exploring structured data extraction and modeling in LLM-driven data pipelines. The project focuses on adding structure to unstructured data using multimodal LLMs (starting with Google Gemini) and experimenting with different data modeling approaches optimized for LLM context and reuse.

This is an exploratory research project, not a production library. The architecture is intentionally kept flexible to support experimentation with multiple approaches.

## Current State

**Phase 1: Foundation** (Current)
- Minimal architecture with direct Gemini API integration
- Pydantic schemas for structured outputs
- Exploratory research mindset - try different approaches

**Phase 2: Storage** (Near-term)
- DuckDB integration for structured data storage
- Hash-based IDs (SHA256) for deterministic identifiers
- Query and retrieval capabilities

**Phase 3: Modeling** (Planned)
- Experiment with multiple modeling approaches:
  - Dimensional modeling (star schema)
  - Graph-based models
  - Hybrid approaches
  - Other patterns as discovered
- Compare effectiveness for LLM context management

**Phase 4: Processors** (Optional)
- Optional genai-processors framework integration
- Complex pipeline compositions if needed
- Not required for core functionality

## Tech Stack

- **Python**: 3.11+
- **Package Management**: `uv` (always use uv for running Python and installing packages)
- **LLM Provider**: Google Gemini (gemini-2.0-flash, gemini-2.5-pro)
- **Core Dependencies**:
  - `google-genai` - Gemini API client
  - `pydantic` - Schema definitions and validation
  - `duckdb` - Columnar database (Phase 2+)
- **Optional Dependencies**:
  - `genai-processors` - Google's processor framework (install via extras)

## Development Commands

### Setup
```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or .venv/Scripts/activate on Windows

# Install package in editable mode with dev dependencies
uv pip install -e ".[dev]"

# Install with optional genai-processors support
uv pip install -e ".[processors,dev]"
```

### Running Code
```bash
# Always use uv to run Python
uv run python src/structure_it/main.py
uv run python examples/extract_recipe.py
```

### Testing
```bash
# Run all tests
uv run pytest tests/

# Run specific test file
uv run pytest tests/test_extractors.py

# Run with coverage
uv run pytest --cov=structure_it tests/
```

### Code Quality
```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type checking
uv run mypy src/
```

## Architecture

### Package Structure
```
src/structure_it/
├── __init__.py           # Package initialization
├── extractors/           # Structured data extraction using Gemini
│   ├── base.py          # Base extractor interface
│   └── gemini.py        # Gemini-specific implementation
├── schemas/              # Pydantic models for structured outputs
│   └── base.py          # Base schema types
├── storage/              # Data persistence (Phase 2+)
│   └── duckdb.py        # DuckDB integration
└── utils/                # Shared utilities
    └── hashing.py       # SHA256-based ID generation
```

### Key Design Principles

1. **Research-Oriented**: This is a sandbox for exploration. Try different approaches, compare results, document findings.

2. **Modular & Extensible**: Components should be loosely coupled. Easy to swap extractors, storage backends, or modeling approaches.

3. **LLM-First Design**:
   - Optimize for LLM context window efficiency
   - Support multimodal inputs (text, images, documents)
   - Structure data for easy LLM consumption and reasoning

4. **Multiple Modeling Approaches**: Don't constrain to one pattern. Compare:
   - Dimensional modeling (facts/dimensions)
   - Graph structures (nodes/edges)
   - Document/collection models
   - Hybrid approaches

5. **Optional Complexity**: Keep core simple. Add genai-processors or complex pipelines only when needed.

### Influenced By

This project draws inspiration from:
- **star-schema-llm-context**: Dimensional modeling for LLM memory, DuckDB usage, hash-based IDs
- **Gemini Structured Outputs**: JSON schema generation, Pydantic integration, streaming
- **genai-processors**: Modular processor architecture, async composition patterns

See `coderef/` directory for detailed reference materials.

## Configuration

### Environment Variables
```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional
STRUCTURE_IT_DB_PATH=./data/structure_it.duckdb
STRUCTURE_IT_LOG_LEVEL=INFO
```

### API Keys
Store API keys in `.env` file (gitignored). Never commit credentials.

## Development Workflow

1. **Iterate Quickly**: Use examples/ directory to test ideas
2. **Document Findings**: Add notes to docs/ or inline comments about what works/doesn't
3. **Version Tracking**: Update CHANGELOG.md (use x.x.x versioning)
4. **No Auto-Commits**: Git commits are manual, not automatic
5. **Stay Focused**: One LLM provider (Gemini) to start - can expand later

## Research Questions to Explore

- How do different modeling approaches (dimensional vs. graph vs. document) affect LLM context efficiency?
- What's the right balance between structure and flexibility?
- When is genai-processors worth the complexity vs. direct API calls?
- How can we optimize for both human and LLM data consumption?
- What patterns emerge for multimodal data structuring?

## References

- [Gemini Structured Outputs](https://blog.google/technology/developers/gemini-api-structured-outputs/)
- [langextract](https://github.com/google/langextract)
- [Star Schema for LLM Context](https://github.com/fblissjr/star-schema-llm-context/)
- [GenAI Processors](https://github.com/google-gemini/genai-processors)`
