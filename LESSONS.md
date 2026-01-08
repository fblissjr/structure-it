# Lessons Learned

Patterns, anti-patterns, and insights discovered during development.

---

## Architecture

### LLM Context Efficiency
**Lesson**: Smaller, focused documents (500-1000 lines) are more effective for LLM consumption than monolithic files.
**Evidence**: IMPLEMENTATION.md at 3,937 lines required constant offset/limit navigation, making it hard to find relevant sections.
**Action**: Split into topical files, create index for navigation.

### Storage Flexibility
**Lesson**: Start with JSON columns in DuckDB, normalize only when patterns emerge from real data.
**Evidence**: Premature schema design led to rework when actual extracted data revealed different patterns than anticipated.
**Action**: Use JSONStorage for prototyping, graduate fields to typed columns only after analyzing extraction results.

### Hash-Based IDs
**Lesson**: Deterministic SHA256-based IDs enable idempotent operations and natural deduplication.
**Evidence**: Re-running extractors on same content produces same entity ID, preventing duplicates without coordination.
**Action**: Always use `generate_entity_id(source_url, entity_type)` for storage operations.

---

## Scraping

### Rate Limiting Strategy
**Lesson**: Static `time.sleep()` is inadequate for polite scraping; use framework-level throttling with adaptive backoff.
**Evidence**: Analysis of production scrapers (heydf) showed token bucket + exponential backoff as standard practice.
**Action**: Adopted Scrapy with built-in DOWNLOAD_DELAY, RANDOMIZE_DOWNLOAD_DELAY, and AUTOTHROTTLE.

### Change Data Capture
**Lesson**: Always check content hash before re-processing to avoid redundant LLM calls.
**Evidence**: Re-scraping unchanged documents wastes API calls and storage.
**Action**: Pipeline checks `storage.check_document_status(entity_id, content_hash)` before extraction.

---

## LLM Extraction

### Prompt Specificity
**Lesson**: Be explicit about what to extract; vague prompts produce inconsistent results.
**Evidence**: Prompts like "extract key information" yielded variable schemas. Specific field lists improved consistency.
**Action**: Define Pydantic schemas with field descriptions; reference fields in prompts.

### Schema Validation
**Lesson**: Let Pydantic catch extraction errors early rather than downstream processing.
**Evidence**: Unvalidated JSON caused silent failures in storage and querying.
**Action**: All extractors return typed Pydantic models; validation errors surface immediately.

---

## Development

### Testing External Services
**Lesson**: Always mock LLM calls in tests to avoid flakiness, costs, and API rate limits.
**Evidence**: Early tests hit actual Gemini API, causing intermittent failures and unexpected charges.
**Action**: Use `unittest.mock` for all Gemini interactions in unit tests.

### Configuration Centralization
**Lesson**: Centralize model names, paths, and settings in one config file.
**Evidence**: Hardcoded model names scattered across files made updates error-prone.
**Action**: All settings in `src/structure_it/config.py`, loaded from environment variables.

---

## Documentation

### Entry Point Pattern
**Lesson**: LLMs work better with a concise entry point document that links to detailed docs.
**Evidence**: 500+ line CLAUDE.md was often skipped in favor of direct file exploration.
**Action**: AGENTS.md as 80-line entry point; docs/INDEX.md for navigation.

### Session Continuity
**Lesson**: Track decisions and context across sessions to avoid repeating analysis.
**Evidence**: Re-exploring same questions across sessions wasted time.
**Action**: SESSION_LOG.md for rolling entries, BACKLOG.md for persistent TODOs.
