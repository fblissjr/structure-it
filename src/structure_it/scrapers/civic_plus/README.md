# CivicPlus Scraper

This module contains a robust **Scrapy** spider for scraping CivicPlus AgendaCenter websites (e.g., Example Village).

It serves as a "Gold Standard" implementation of our scraping strategy, replacing the need for raw `requests` loops or unmaintained libraries like `civic-scraper`.

## Architecture

*   **Spiders**:
    *   `spider.py`: Crawls **AgendaCenter** to find meeting Agendas, Minutes, Packets, Audio, and Video.
    *   `bids_spider.py`: Crawls **Bids.aspx** to find Bid/RFP summaries and associated PDF specifications.
    *   **`services_spider.py`**: Crawls **RequestTracker.aspx** to extract service request logs.
    *   `permits_spider.py`: Crawls **DocumentCenter** folders to find Building Permit reports or Financial Reports (Budget/CAFR).
    *   **Safety**: Configured with `AutoThrottle`, `DOWNLOAD_DELAY` (2s), and a custom `USER_AGENT`.
*   **Pipeline (`pipelines.py`)**: Handles the processing phase.
    *   **Smart Download**: 
        *   Checks file size (HEAD request) to skip huge files (>100MB).
        *   **Viewer Unwrapping**: Detects HTML viewer pages acting as wrappers for PDFs and automatically finds the real download link.
    *   **CDC (Change Data Capture)**: Hashes the file content and checks `StarSchemaStorage` to see if it's new. If identical to a previous version, it skips further processing.
    *   **Extraction**: If new, converts to Markdown (`MarkItDown`) and sends to Gemini (`GeminiExtractor`). Dynamically selects the appropriate schema (`CivicMeeting`, `CivicBid`, etc.) based on source.
    *   **Storage**: Saves the result to DuckDB (Star Schema).

## Usage

Use the runner script in `examples/` with the `--spider` argument:

```bash
# Scrape Agendas/Minutes (Default)
uv run python examples/run_scrapy_civic.py --spider agenda

# Scrape Bids/RFPs
uv run python examples/run_scrapy_civic.py --spider bids --url "https://example.com/Bids.aspx"

# Scrape Service Requests
uv run python examples/run_scrapy_civic.py --spider services --url "https://example.com/RequestTracker.aspx"

# Scrape Building Permits
uv run python examples/run_scrapy_civic.py --spider permits --doc-type permit --url "https://example.com/DocumentCenter/Index/123"

# Scrape Financial Reports
uv run python examples/run_scrapy_civic.py --spider permits --doc-type financial --url "https://example.com/DocumentCenter/Index/456"
```

## Customization

To scrape a different village:

```python
from structure_it.scrapers.civic_plus.spider import CivicPlusSpider
process.crawl(CivicPlusSpider, place_url="https://your-village.com/AgendaCenter")
```
