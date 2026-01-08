# Scraping Architecture

Scrapy integration and rate limiting strategy for structure-it.

## Why Scrapy

Scrapy was adopted over simple `requests` loops for several reasons:

1. **Built-in Politeness**: DOWNLOAD_DELAY, AUTOTHROTTLE, CONCURRENT_REQUESTS
2. **Robust Error Handling**: Automatic retries, backoff
3. **Structured Pipelines**: Clean separation of scraping from processing
4. **Extensibility**: Easy to add new spiders for different sources
5. **Performance**: Async I/O, connection pooling

## Spider Architecture

```
examples/run_scrapy_civic.py
           |
           v
  +-----------------+
  | CrawlerProcess  |
  +-----------------+
           |
           v
  +-----------------+
  |   Spider        |  <- CivicPlusSpider, BidsSpider, etc.
  +-----------------+
           |
           v
  +-----------------+
  | Pipeline        |  <- StructureItPipeline
  +-----------------+
           |
           v
  +-----------------+
  | Storage         |  <- StarSchemaStorage / DuckDB
  +-----------------+
```

## Available Spiders

| Spider | Module | Target | Rate Limiting |
|--------|--------|--------|---------------|
| `CivicPlusSpider` | AgendaCenter | Meeting agendas/minutes | Conservative (10s) |
| `CivicPlusBidsSpider` | Bids.aspx | Procurement/RFPs | Moderate (2s) |
| `CivicPlusServicesSpider` | RequestTracker | Service requests | Moderate (2s) |
| `CivicPlusPermitsSpider` | DocumentCenter | Permits/Financials | Moderate (2s) |

## Rate Limiting Settings

### AgendaCenter Spider (Conservative)

```python
CONCURRENT_REQUESTS = 1           # Single request at a time
DOWNLOAD_DELAY = 10.0             # 10 seconds between requests
RANDOMIZE_DOWNLOAD_DELAY = True   # Add randomness (0-10s extra)
AUTOTHROTTLE_ENABLED = True       # Adaptive throttling
AUTOTHROTTLE_START_DELAY = 2.0
AUTOTHROTTLE_MAX_DELAY = 60.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
```

### Other Spiders (Moderate)

```python
CONCURRENT_REQUESTS = 4           # 4 concurrent requests
DOWNLOAD_DELAY = 2.0              # 2 seconds between requests
RANDOMIZE_DOWNLOAD_DELAY = True   # Add randomness
AUTOTHROTTLE_ENABLED = True       # Adaptive throttling
AUTOTHROTTLE_START_DELAY = 2.0
AUTOTHROTTLE_MAX_DELAY = 60.0
```

## Pipeline Processing

The `StructureItPipeline` implements a 5-phase workflow:

### Phase 1: Content Download
- Validates file size before download (max 100MB)
- Downloads to `temp_downloads/` directory
- Handles viewer page unwrapping

### Phase 2: Content Conversion
- Uses MarkItDown for PDF/HTML to Markdown
- Runs in thread pool for CPU-bound conversion

### Phase 3: CDC Check
- Computes SHA256 hash of content
- Calls `storage.check_document_status(entity_id, content_hash)`
- Skips processing if content unchanged

### Phase 4: LLM Extraction
- Selects extractor based on `source_type`
- Uses domain-specific Pydantic schema
- Calls Gemini API with structured output

### Phase 5: Storage
- Stores to DuckDB (Star Schema)
- Generates deterministic entity ID

## User-Agent

All spiders use an identifiable User-Agent:

```
CivicDataBot/1.0 (+https://github.com/fredbliss/structure-it)
```

## CLI Configuration

The runner script (`examples/run_scrapy_civic.py`) supports CLI overrides:

```bash
# Preview settings
uv run python examples/run_scrapy_civic.py --url URL --dry-run

# Limit items
uv run python examples/run_scrapy_civic.py --url URL --limit 5

# Custom throttling
uv run python examples/run_scrapy_civic.py --url URL --delay 15 --concurrent 1
```

## Best Practices

1. **Always test with `--limit 1`** before full scrapes
2. **Use `--dry-run`** to preview settings
3. **Monitor logs** for rate limit responses (429)
4. **Start conservative**, relax throttling if server handles it
5. **Check robots.txt** for target sites

## Related

- [Civic Data Guide](../guides/civic-data.md) - Usage and schemas
- [Storage Architecture](storage.md) - CDC implementation
