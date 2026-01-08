# Architecture Overview

Project structure, tech stack, and design principles for structure-it.

## Purpose

structure-it is a research sandbox for structured data extraction using multimodal LLMs (Gemini). It extracts structured data from unstructured content (PDFs, web pages, documents) and stores it in queryable formats.

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Runtime | Python 3.11+ | Core language |
| Package Manager | uv | Dependency management |
| LLM | Google Gemini | Extraction engine |
| Database | DuckDB | Analytical storage |
| Validation | Pydantic | Schema definition |
| Scraping | Scrapy | Web data collection |
| Frontend | React + Vite | Structure Studio UI |
| Styling | Tailwind CSS | UI theming |

## Package Structure

```
src/structure_it/
  __init__.py           # Package initialization
  config.py             # Centralized configuration
  extractors/           # LLM-powered extraction
  scrapers/             # Scrapy spiders (CivicPlus)
  generators/           # Synthetic content generation
  schemas/              # Pydantic models
  storage/              # DuckDB + JSON backends
  utils/                # Hashing, helpers
```

## Key Components

### Extractors
LLM-powered structured data extraction from unstructured content.
- `GeminiExtractor`: Base extractor using Gemini API
- `PolicyRequirementsExtractor`: Domain-specific for policy docs

### Storage
Flexible backends for storing extracted data.
- `JSONStorage`: File-based, human-readable
- `DuckDBStorage`: Queryable with JSON columns
- `StarSchemaStorage`: Dimensional model for analytics

### Scrapers
Scrapy-based data collection with CDC (Change Data Capture).
- `CivicPlusSpider`: Municipal agendas/minutes
- `CivicPlusBidsSpider`: Procurement/RFPs
- `CivicPlusServicesSpider`: Service requests
- `CivicPlusPermitsSpider`: Building permits

### Schemas
Pydantic models for structured output validation.
- 6 domain-specific schemas implemented
- All inherit from `BaseSchema`
- Strict typing with optional fields

## Design Principles

1. **Research-Oriented**: Sandbox for exploration, not production library
2. **Modular & Extensible**: Loosely coupled, easy to swap components
3. **LLM-First Design**: Optimize for context window efficiency
4. **Flexible Storage**: JSON-first, normalize when patterns emerge
5. **Optional Complexity**: Keep core simple, add sophistication as needed

## Data Flow

```
Input (PDF/HTML/Text)
        |
        v
   [Preprocessing]
   (markitdown conversion)
        |
        v
   [Extraction]
   (GeminiExtractor + Pydantic schema)
        |
        v
   [Storage]
   (DuckDB + JSON with SHA256 ID)
        |
        v
   [Retrieval]
   (Query by source_type, entity_id, filters)
```

## Configuration

All settings centralized in `src/structure_it/config.py`:

```python
STRUCTURE_IT_MODEL      # Default: gemini-2.5-flash
STRUCTURE_IT_TEMPERATURE # Default: 0.8
STRUCTURE_IT_DB_PATH    # Default: ./data/structure_it.duckdb
GOOGLE_API_KEY          # Required
```

## Related Documentation

- [Storage Architecture](storage.md) - Star Schema, CDC, DuckDB patterns
- [Scraping Strategy](scraping.md) - Scrapy integration, rate limiting
- [Star Schema Details](star-schema.md) - Dimensional Context Model
- [Graph Modeling](graph-modeling.md) - Relationship storage patterns
