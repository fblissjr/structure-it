# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0]

### Added

**Core Infrastructure**:
- Initial project structure and foundational architecture
- Base extractor interface for structured data extraction
- Gemini extractor implementation using Google Gemini API
- Base schema class for Pydantic models
- Package structure: extractors, schemas, storage, utils
- Development tooling: pytest, ruff, mypy

**Storage Layer**:
- Flexible storage abstraction supporting multiple backends
- JSON file storage backend (simple, human-readable)
- DuckDB storage backend (analytical queries, efficient)
- SHA256-based deterministic ID generation (inspired by star-schema-llm-context)
- Thread-safe storage operations

**Domain Schemas**:
- Academic paper extraction schema (authors, citations, sections, findings)
- Code documentation schema (functions, classes, parameters, examples)
- Meeting transcript schema (participants, decisions, action items)
- Media transcript schema (YouTube/podcast: speakers, segments, timestamps)
- Web article schema (author, content, key points, technologies mentioned)

**Web Content Extraction**:
- markitdown integration for HTML to markdown conversion
- Web article extraction example with full pipeline
- Academic paper extraction example (PDF/URL support)

**Examples**:
- Recipe extraction from text (original demo)
- Web article extraction with storage demonstration
- Academic paper extraction with markitdown

**Documentation**:
- CLAUDE.md with comprehensive project guidance
- Phase-based roadmap (Phase 1-4)
- GenAI processors analysis and integration guidelines
- LangExtract analysis and evaluation

**Research Foundation**:
- Optional genai-processors integration support
- Exploration documents for library evaluations
- Multi-domain extraction support for research comparisons
