# Documentation Index

Navigation hub for all structure-it documentation.

---

## Architecture

| Document | Purpose |
|----------|---------|
| [overview.md](architecture/overview.md) | Project structure, tech stack, design principles |
| [storage.md](architecture/storage.md) | Star Schema, CDC, DuckDB patterns |
| [scraping.md](architecture/scraping.md) | Scrapy integration, rate limiting |
| [star-schema.md](architecture/star-schema.md) | Dimensional Context Model details |
| [graph-modeling.md](architecture/graph-modeling.md) | Relationship storage patterns |

## Implementation Patterns

| Document | Purpose |
|----------|---------|
| [extraction-patterns.md](implementation/extraction-patterns.md) | Multi-stage, chunked, hierarchical extraction |
| [context-assembly.md](implementation/context-assembly.md) | Token optimization, serialization |
| [rag-patterns.md](implementation/rag-patterns.md) | Vector storage, embeddings, hybrid search |
| [schema-evolution.md](implementation/schema-evolution.md) | Versioning, migration strategies |
| [quality-validation.md](implementation/quality-validation.md) | Metrics, confidence scoring |
| [incremental-processing.md](implementation/incremental-processing.md) | CDC, differential updates |
| [multimodal.md](implementation/multimodal.md) | PDF, image, audio/video extraction |
| [cross-domain.md](implementation/cross-domain.md) | Pattern analysis across domains |

## Guides

| Document | Purpose |
|----------|---------|
| [testing.md](guides/testing.md) | pytest patterns, mocking strategies |
| [civic-data.md](guides/civic-data.md) | CivicPlus scraping, schemas, pipelines |

## Planning

| Document | Purpose |
|----------|---------|
| [roadmap.md](roadmap.md) | Vision, phases, research questions |

---

## Quick Links

- **Entry Point**: [AGENTS.md](../AGENTS.md)
- **Session Tracking**: [SESSION_LOG.md](../SESSION_LOG.md), [BACKLOG.md](../BACKLOG.md), [LESSONS.md](../LESSONS.md)
- **Research**: [explorations/](../explorations/)
- **Config**: `src/structure_it/config.py`
