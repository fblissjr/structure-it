# AGENTS.md

Research sandbox for structured data extraction using multimodal LLMs.

## Quick Reference

```bash
uv run python <script>      # Run Python
uv add <package>            # Install package
uv run pytest tests/        # Run tests
./start.sh                  # Full stack (UI + API)
```

## Configuration

```bash
export GOOGLE_API_KEY="your-key"                      # Required
export STRUCTURE_IT_MODEL="gemini-3-flash-preview"    # Optional (default)
```

Config source: `src/structure_it/config.py`

## Project Structure

```
src/structure_it/
  config.py       # Centralized settings (model, paths)
  extractors/     # LLM-powered extraction (GeminiExtractor)
  schemas/        # Pydantic models for structured output
  storage/        # DuckDB + JSON backends
  scrapers/       # Scrapy spiders (CivicPlus example)
  generators/     # Synthetic content generation

examples/         # Runnable extraction examples
docs/             # Full documentation
explorations/     # Research notes
```

## Core Pattern

```python
from structure_it.extractors import GeminiExtractor
from structure_it.schemas.articles import WebArticle

extractor = GeminiExtractor(schema=WebArticle)
result = await extractor.extract(content, prompt="Extract article info")
```

## Documentation

- [docs/INDEX.md](docs/INDEX.md) - Full navigation
- [docs/roadmap.md](docs/roadmap.md) - Vision and research questions

## Session Tracking

- [SESSION_LOG.md](SESSION_LOG.md) - Rolling session log
- [BACKLOG.md](BACKLOG.md) - Cross-session TODOs
- [LESSONS.md](LESSONS.md) - Patterns learned

## Constraints

- Use `uv` for Python (never pip)
- No automatic git commits
- No emojis in output
- Semantic versioning in CHANGELOG.md (no dates)
