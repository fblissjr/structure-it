# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**structure-it** is a research sandbox for exploring structured data extraction and modeling in LLM-driven data pipelines. The project focuses on adding structure to unstructured data using multimodal LLMs (starting with Google Gemini) and experimenting with different data modeling approaches optimized for LLM context and reuse.

This is an exploratory research project, not a production library. The architecture is intentionally kept flexible to support experimentation with multiple approaches.

## Current State

**Phase 1: Foundation** ✅ COMPLETE
- Direct Gemini API integration via `google-genai`
- Base extractor interface and GeminiExtractor implementation
- Pydantic schemas for structured outputs
- Multi-domain support (5 schemas implemented)

**Phase 2: Storage** ✅ COMPLETE
- Flexible storage abstraction with multiple backends
- JSON file storage (simple, human-readable)
- DuckDB storage (analytical queries, efficient)
- SHA256-based deterministic ID generation
- Full CRUD operations (store, retrieve, query, delete, count)

**Phase 3: Modeling** 🔄 READY TO START
- Infrastructure in place for experimentation
- Ready to extract real data across domains
- Compare JSON flexibility vs. DuckDB structure
- Document patterns that emerge from real data
- Planned experiments:
  - Extract 5-10 examples per domain
  - Query and analyze stored data
  - Identify common vs. domain-specific patterns
  - Iterate on schema design based on findings
  - Potentially explore star schema or graph models

**Phase 4: Processors** ⏸️ DEFERRED
- Optional genai-processors framework integration
- Analysis complete (see `explorations/genai-processors-analysis.md`)
- Decision: Not needed for current research goals
- Will revisit if complex pipelines emerge

## Tech Stack

- **Python**: 3.11+ (3.13 recommended)
- **Package Management**: `uv` (always use uv for running Python and installing packages)
- **LLM Provider**: Google Gemini (default: `gemini-2.5-flash`, configurable via `STRUCTURE_IT_MODEL`)
- **Core Dependencies**:
  - `google-genai` (1.49.0+) - Gemini API client
  - `pydantic` (2.12.4+) - Schema definitions and validation
  - `pydantic-settings` - Environment configuration
  - `duckdb` (1.4.1+) - Columnar analytical database
  - `markitdown` (0.1.3+) - HTML to Markdown conversion for web articles and PDFs
  - `python-dotenv` - Environment variable management
- **Development Dependencies**:
  - `pytest` + `pytest-asyncio` + `pytest-cov` - Testing
  - `ruff` - Linting and formatting
  - `mypy` - Type checking
- **Optional Dependencies**:
  - `genai-processors` - Google's processor framework (not currently used)

## Configuration

All model defaults and settings are centralized in `src/structure_it/config.py`:

```bash
# Model configuration (defaults to gemini-2.5-flash)
export STRUCTURE_IT_MODEL="gemini-2.5-flash"  # or gemini-2.5-pro for higher quality

# Generation settings
export STRUCTURE_IT_TEMPERATURE="0.8"

# Storage paths
export STRUCTURE_IT_DB_PATH="./data/structure_it.duckdb"
export STRUCTURE_IT_JSON_PATH="./data/entities"

# API key (required)
export GOOGLE_API_KEY="your-api-key-here"
```

No more hunting for hardcoded model names! Everything respects these environment variables.

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

### Running Examples
```bash
# Always use uv to run Python
# Set your API key first: export GOOGLE_API_KEY='your-key-here'

# Extract recipe from text (original demo)
uv run python examples/extract_recipe.py

# Extract web article from URL (with storage demo)
uv run python examples/extract_web_article.py https://python.org/about/

# Extract academic paper from PDF or URL
uv run python examples/extract_academic_paper.py paper.pdf
uv run python examples/extract_academic_paper.py https://arxiv.org/abs/2301.00001

# Extract policy requirements from PDF
uv run python examples/extract_policy_requirements.py policy.pdf \
  --policy-id FIN-001 \
  --policy-title "Expense Reimbursement Policy" \
  --policy-type Financial
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
├── __init__.py                 # Package initialization
├── config.py                   # Centralized configuration (model defaults, paths)
├── extractors/                 # Structured data extraction
│   ├── __init__.py
│   ├── base.py                # Base extractor interface
│   ├── gemini.py              # Gemini API implementation (uses config)
│   └── policy_extractor.py    # Policy requirements extractor (PDF/markdown → requirements)
├── generators/                 # LLM-powered content generation
│   ├── __init__.py
│   ├── base.py                # BaseGenerator for reusable generation logic
│   ├── policy.py              # PolicyGenerator for policy documents
│   ├── arxiv.py               # ArxivGenerator for AI/ML research papers
│   └── civic.py               # CivicDocumentGenerator for government docs
├── schemas/                    # Pydantic models for structured outputs (6 domains)
│   ├── __init__.py
│   ├── base.py                # Base schema class
│   ├── academic.py            # Academic papers
│   ├── articles.py            # Web articles/blogs
│   ├── code_docs.py           # Code documentation
│   ├── meetings.py            # Meeting transcripts
│   ├── media.py               # YouTube/podcast transcripts
│   └── policy_requirements.py # Policy requirements (example domain-specific schema)
├── storage/                    # Data persistence backends
│   ├── __init__.py
│   ├── base.py                # Abstract storage interface
│   ├── json_storage.py        # JSON file backend
│   └── duckdb_storage.py      # DuckDB backend
└── utils/                      # Shared utilities
    ├── __init__.py
    └── hashing.py             # SHA256-based deterministic ID generation
```

**Key Components:**
- **config.py**: Single source of truth for model names, temperature, paths
- **extractors/**: Extract structured data from unstructured content (core capability)
- **generators/**: Generate synthetic content for testing extraction (reusable base class)
- **schemas/**: Domain-specific Pydantic models (policy extraction is just one example)
- **storage/**: Flexible backends for storing extracted data

### Examples Directory
```
examples/
├── extract_recipe.py               # Recipe extraction (original demo)
├── extract_web_article.py          # Web article with markitdown + storage
├── extract_academic_paper.py       # Academic paper from PDF/URL
└── extract_policy_requirements.py  # Policy requirements from PDFs
```

### Scripts Directory
```
scripts/
├── generate_micro_dataset.py     # Generate 3-policy test dataset
├── generate_full_dataset.py      # Generate 13-policy comprehensive dataset
├── generate_metadata_only.py     # Generate policy metadata without API calls
├── generate_arxiv_dataset.py     # Generate 8 AI/ML ArXiv papers
└── generate_civic_dataset.py     # Generate 8 civic/government documents
```

All scripts use the BaseGenerator pattern, demonstrating extensibility across domains.

### Explorations Directory
```
explorations/
├── genai-processors-analysis.md  # Analysis of genai-processors framework
├── langextract-analysis.md       # Analysis of langextract library
└── policy/                       # Policy requirements exploration (one domain example)
    ├── policy_project.md         # Project plan for policy extraction system
    └── policy_dataset.md         # Dataset strategy for testing
```

### Documentation
```
docs/
└── policy_requirements_guide.md  # Detailed guide for policy extraction use case
```

For other use cases (web articles, academic papers, etc.), examples demonstrate patterns
without requiring separate guides. Create domain-specific docs as needed.

### Implementation Details

**Extraction Pipeline**:
1. **Input**: Raw content (text, URL, PDF, markdown)
2. **Conversion**: Optional preprocessing (e.g., markitdown for HTML → markdown)
3. **Extraction**: GeminiExtractor with Pydantic schema → structured output
4. **Storage**: Save to JSON and/or DuckDB with SHA256 entity ID
5. **Retrieval**: Query by source type, entity ID, or custom filters

**Generator Architecture**:
- **BaseGenerator**: Reusable LLM-powered content generation
  - Centralized model/temperature management via config
  - Async text generation with customizable prompts
  - Save output as markdown/JSON/etc
  - Extensible for any domain
- **Domain-Specific Generators** (extend BaseGenerator):
  - **PolicyGenerator**: Policy documents (5 domains: Financial, IT, HR, Legal, Compliance)
  - **ArxivGenerator**: AI/ML research papers (6 focus areas: ML, CV, NLP, Robotics, etc.)
  - **CivicDocumentGenerator**: Local government docs (agendas, minutes, proposals, resolutions)
  - Easy to add more: ArticleGenerator, CodeDocGenerator, etc.

**Storage Architecture**:
- **BaseStorage**: Abstract interface for storage backends
- **JSONStorage**: File-based storage in `./data/entities/{hash[:2]}/{hash}.json`
  - Simple, human-readable
  - Good for prototyping and small datasets
  - No schema enforcement
- **DuckDBStorage**: Database storage in `./data/structure_it.duckdb`
  - Flexible JSON columns for structured data
  - Indexed queries by source_type, created_at
  - Analytical queries and aggregations
  - Schema: `extracted_entities` table with JSON fields

**Hash-Based IDs** (inspired by star-schema-llm-context):
- Deterministic SHA256 hashes
- `generate_entity_id(source_url, entity_type)` → unique ID
- Same source always gets same ID (idempotent)
- No auto-increment, no coordination needed
- Natural deduplication

**Domain Schemas** (6 implemented):
1. **AcademicPaper**: Title, authors, abstract, sections, citations, findings
2. **WebArticle**: Title, author, content, key points, technologies mentioned
3. **CodeDocumentation**: Functions, classes, parameters, examples, cross-references
4. **MeetingNote**: Participants, decisions, action items, topics discussed
5. **MediaTranscript**: YouTube/podcast with speakers, segments, timestamps
6. **PolicyRequirements**: Requirements extraction from policy/procedure documents
   - Individual requirements with classification (mandatory/recommended/prohibited)
   - Applicability tracking (roles, conditions, exceptions)
   - Regulatory basis capture (SOX, GDPR, etc.)
   - Domain-specific extraction for Financial, IT Security, HR, Legal, Compliance

All schemas inherit from `BaseSchema` with:
- Pydantic validation
- `to_dict()` and `to_json()` methods
- Strict typing with optional fields
- Extra fields forbidden

### Key Design Principles

1. **Research-Oriented**: This is a sandbox for exploration. Try different approaches, compare results, document findings.

2. **Modular & Extensible**: Components should be loosely coupled. Easy to swap extractors, storage backends, or modeling approaches.

3. **LLM-First Design**:
   - Optimize for LLM context window efficiency
   - Support multimodal inputs (text, images, documents)
   - Structure data for easy LLM consumption and reasoning

4. **Flexible Storage**: JSON-first approach - let structure emerge from data rather than forcing it upfront.
   - Store structured data as JSON
   - Normalize when patterns emerge
   - Compare JSON flexibility vs. typed columns

5. **Optional Complexity**: Keep core simple. Add genai-processors or complex pipelines only when needed.

### Influenced By

This project draws inspiration from:
- **star-schema-llm-context**: Dimensional modeling for LLM memory, DuckDB usage, hash-based IDs
  - Adopted: SHA256-based IDs, DuckDB storage
  - Deferred: Star schema modeling (may explore in Phase 3)
- **Gemini Structured Outputs**: JSON schema generation, Pydantic integration, streaming
  - Adopted: Pydantic schemas with structured output API
  - Core to our extraction approach
- **genai-processors**: Modular processor architecture, async composition patterns
  - Evaluated: See `explorations/genai-processors-analysis.md`
  - Decision: Deferred - too complex for current needs
- **langextract**: Entity extraction with source grounding
  - Evaluated: See `explorations/langextract-analysis.md`
  - Decision: Deferred - scope mismatch with our goals

See `coderef/` directory for detailed reference materials.

## Usage Patterns

### Basic Extraction
```python
import asyncio
from structure_it.extractors import GeminiExtractor
from structure_it.schemas.articles import WebArticle

async def extract_article(url: str):
    # Create extractor with schema
    extractor = GeminiExtractor(schema=WebArticle)

    # Extract structured data
    article = await extractor.extract(
        content=markdown_content,
        prompt="Extract article information including title, author, key points."
    )

    return article

# Run
article = asyncio.run(extract_article("https://example.com"))
print(article.to_json())
```

### Storage Usage
```python
from structure_it.storage import JSONStorage, DuckDBStorage
from structure_it.utils import generate_entity_id

# Choose storage backend
json_storage = JSONStorage()           # Simple files
duckdb_storage = DuckDBStorage()       # Analytical queries

# Generate deterministic ID
entity_id = generate_entity_id(url, "web_article")

# Store
await json_storage.store_entity(
    entity_id=entity_id,
    source_type="web_article",
    source_url=url,
    raw_content=markdown,
    structured_data=article.to_dict(),
    metadata={"model": "gemini-2.0-flash-exp"}
)

# Query
articles = await duckdb_storage.query_entities(
    source_type="web_article",
    limit=10
)

# Count
total = await duckdb_storage.count_entities()
```

### Creating Custom Schemas
```python
from structure_it.schemas.base import BaseSchema

class CustomSchema(BaseSchema):
    """Your custom extraction schema."""

    title: str
    main_content: str
    tags: list[str] = []
    metadata: dict[str, Any] = {}

# Use with extractor
extractor = GeminiExtractor(schema=CustomSchema)
result = await extractor.extract(content, prompt="...")
```

### Web Content Extraction
```python
from markitdown import MarkItDown

# Convert web page to markdown
md = MarkItDown()
result = md.convert("https://example.com/article")
markdown = result.text_content

# Extract structured data
extractor = GeminiExtractor(schema=WebArticle)
article = await extractor.extract(markdown)
```

### Policy Requirements Extraction
```python
from structure_it.extractors import PolicyRequirementsExtractor

# Extract requirements from policy PDF
extractor = PolicyRequirementsExtractor()

requirements = await extractor.extract(
    pdf_path="expense_policy.pdf",
    policy_metadata={
        "policy_id": "FIN-001",
        "policy_title": "Expense Reimbursement Policy",
        "policy_type": "Financial",
        "policy_version": "1.0",
        "effective_date": "2024-01-15",
    }
)

# Access extracted requirements
print(f"Total: {requirements.total_requirements}")
print(f"Mandatory: {requirements.total_mandatory}")
print(f"Recommended: {requirements.total_recommended}")

for req in requirements.requirements:
    print(f"{req.requirement_type}: {req.statement}")
    if req.applies_to:
        print(f"  Applies to: {', '.join(req.applies_to)}")
    if req.regulatory_basis:
        print(f"  Regulatory: {', '.join(req.regulatory_basis)}")
```

## Tips for Development

### Extraction Best Practices
1. **Clear prompts**: Be specific about what to extract
2. **Schema design**: Start minimal, add fields as needed
3. **Validation**: Let Pydantic catch issues early
4. **Iteration**: Run on real data, refine schemas

### Storage Best Practices
1. **Use JSON storage** for prototyping and inspection
2. **Use DuckDB** when you need queries and analytics
3. **Store in both** during research to compare
4. **Hash IDs** ensure idempotent storage

### Research Workflow
1. Extract a few examples manually
2. Inspect the JSON output
3. Refine schema based on what you see
4. Extract more examples
5. Query DuckDB to find patterns
6. Document findings in explorations/

### Common Issues
- **Token limits**: Long documents may hit limits (future: implement chunking)
- **API errors**: Check GOOGLE_API_KEY environment variable
- **Schema mismatches**: Pydantic will raise ValidationError if extraction doesn't match schema
- **Storage paths**: Default is `./data/` - configure via environment variables if needed

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

## What's Been Built

### Completed Infrastructure
- ✅ Base extractor interface with async support
- ✅ GeminiExtractor with structured output API + centralized config
- ✅ Flexible storage abstraction (JSON + DuckDB backends)
- ✅ SHA256-based deterministic IDs
- ✅ 6 domain-specific Pydantic schemas
- ✅ markitdown integration for web content and PDFs
- ✅ 4 working examples (recipe, web article, academic paper, policy requirements)
- ✅ Development tooling (pytest, ruff, mypy)
- ✅ BaseGenerator + 3 domain generators (policy, arxiv, civic)
- ✅ Sample datasets: 13 policies, 8 ArXiv papers, 8 civic documents
- ✅ Comprehensive test suite (33 tests passing)
- ✅ Data organized in ./data/ directory

### Completed Analysis
- ✅ **genai-processors**: Evaluated Google's pipeline framework
  - Decision: Deferred - too complex for current needs
  - See `explorations/genai-processors-analysis.md`
- ✅ **langextract**: Evaluated Google's entity extraction library
  - Decision: Deferred - scope mismatch (entity vs. generic extraction)
  - See `explorations/langextract-analysis.md`
- ✅ **markitdown**: Adopted for HTML → markdown conversion

### Ready for Phase 3

**Goal**: Extract real data, discover patterns, iterate on schemas

**Next Steps**:
1. Extract 5-10 examples from each domain:
   - Web articles from different sources (tech blogs, news, tutorials)
   - Academic papers from different fields (ML, systems, theory)
   - Code documentation (Python, JavaScript, different styles)
   - Meeting transcripts (standup, planning, retrospective)
   - Media transcripts (YouTube tech talks, podcasts)

2. Analyze stored data:
   - Query DuckDB to find patterns in JSON structures
   - Which fields are consistently populated?
   - Which are sparse or domain-specific?
   - How does structure vary within domains?

3. Document findings:
   - Create `explorations/json-patterns-analysis.md`
   - Create `explorations/schema-evolution.md`
   - Compare JSON vs. DuckDB trade-offs

4. Iterate on schemas based on real data

## Development Workflow

1. **Iterate Quickly**: Use examples/ directory to test ideas
2. **Document Findings**: Add exploration documents for analysis and decisions
3. **Version Tracking**: Update CHANGELOG.md (use x.x.x versioning)
4. **No Auto-Commits**: Git commits are manual, not automatic
5. **Stay Focused**: One LLM provider (Gemini) to start - can expand later
6. **Research First**: Extract real data before making architecture decisions

## Research Questions

### Answered (Phase 1-2)
- ✅ **Is genai-processors worth the complexity vs. direct API calls?**
  - Answer: No, for our use case. Direct API is simpler and clearer for research.
  - See: `explorations/genai-processors-analysis.md`

- ✅ **Should we use langextract for entity extraction?**
  - Answer: No, scope mismatch. We need generic schemas, not just entities.
  - See: `explorations/langextract-analysis.md`

- ✅ **How should we structure storage?**
  - Answer: Flexible abstraction with JSON + DuckDB backends. Let patterns emerge.
  - Implementation: `storage/` with both backends implemented.

### Exploring (Phase 3)
- 🔄 **What patterns emerge from real data across domains?**
  - Need to extract 5-10 examples per domain
  - Analyze what fields are consistently populated
  - Document patterns in `explorations/json-patterns-analysis.md`

- 🔄 **What's the right balance between structure and flexibility?**
  - JSON storage allows flexibility
  - When should we normalize into typed columns?
  - How do schemas evolve based on real data?

- 🔄 **How do different storage approaches affect queryability?**
  - JSON files: simple, readable, no schema
  - DuckDB with JSON columns: queryable but flexible
  - Future: Fully normalized tables vs. JSON columns

### Future (Phase 4+)
- ⏸️ **How do different modeling approaches (dimensional vs. graph vs. document) affect LLM context efficiency?**
  - Will explore after gathering real data
  - May implement star schema if patterns warrant it
  - Graph models for relationship-heavy domains?

- ⏸️ **How can we optimize for both human and LLM data consumption?**
  - Depends on patterns discovered
  - May need context assembly strategies

- ⏸️ **What patterns emerge for multimodal data structuring?**
  - Need more multimodal examples (PDFs with images, videos, etc.)

## References

- [Gemini Structured Outputs](https://blog.google/technology/developers/gemini-api-structured-outputs/)
- [langextract](https://github.com/google/langextract)
- [Star Schema for LLM Context](https://github.com/fblissjr/star-schema-llm-context/)
- [GenAI Processors](https://github.com/google-gemini/genai-processors)`
