# Civic Data Guide

Extracting structured data from local government websites using Scrapy and Gemini.

## Overview

The civic data pipeline:
1. **Collection**: Scrapy spiders crawl CivicPlus modules
2. **Ingestion**: Downloads documents, handles large files, unwraps viewer pages
3. **CDC**: Content hashing to skip unchanged documents
4. **Extraction**: Gemini extracts structured data using domain-specific schemas
5. **Storage**: DuckDB (Star Schema) and JSON

## Data Source Inventory

| Module | URL Pattern | Schema | Status |
|--------|-------------|--------|--------|
| Meetings | `/AgendaCenter` | `CivicMeeting` | Implemented |
| Procurement | `/Bids.aspx` | `CivicBid` | Implemented |
| Services | `/RequestTracker.aspx` | `CivicServiceRequest` | Implemented |
| Permits | `/DocumentCenter/Index/[ID]` | `BuildingPermit` | Implemented |
| Financials | `/DocumentCenter/View/[ID]` | `CivicFinancialReport` | Implemented |
| Notices | `/RSS.aspx` | `CivicNotice` | Planned |

## Schemas

Defined in `src/structure_it/schemas/civic.py`.

### CivicMeeting
Government proceedings (agendas, minutes).
- **Metadata**: Body, Date, Meeting Type
- **Content**: Agenda Items, Roll Call Votes, Public Comments
- **Artifacts**: Links to Packets, Audio, Video

### CivicBid
Procurement opportunities (RFPs, bids).
- **Metadata**: Bid ID, Title, Status (Open/Closed)
- **Content**: Scope of Work, Timeline
- **Artifacts**: Bid Specifications (PDFs)

### CivicServiceRequest
Citizen service requests (311).
- **Metadata**: Request ID, Category, Status, Submission Date
- **Content**: Description, Location

### BuildingPermit
Monthly permit reports.
- **Entities**: Applicant, Contractor, Address
- **Financials**: Valuation, Fees

### CivicFinancialReport
Fiscal documents (CAFR, Budget).
- **Metadata**: Fiscal Year, Report Type
- **Content**: Executive Summaries, Fund Balances

## Spiders

| Spider | Target | Command Flag |
|--------|--------|--------------|
| `CivicPlusSpider` | AgendaCenter | `--spider agenda` |
| `CivicPlusBidsSpider` | Bids.aspx | `--spider bids` |
| `CivicPlusServicesSpider` | RequestTracker.aspx | `--spider services` |
| `CivicPlusPermitsSpider` | DocumentCenter | `--spider permits` |

Location: `src/structure_it/scrapers/civic_plus/`

## Running Scrapers

Entry point: `examples/run_scrapy_civic.py`

```bash
# Meetings (agendas, minutes)
uv run python examples/run_scrapy_civic.py \
  --spider agenda \
  --url "https://example.gov/AgendaCenter"

# Bids & RFPs
uv run python examples/run_scrapy_civic.py \
  --spider bids \
  --url "https://example.gov/Bids.aspx"

# Service Requests (311)
uv run python examples/run_scrapy_civic.py \
  --spider services \
  --url "https://example.gov/RequestTracker.aspx"

# Building Permits
uv run python examples/run_scrapy_civic.py \
  --spider permits \
  --doc-type permit \
  --url "https://example.gov/DocumentCenter/Index/123"

# Financial Reports
uv run python examples/run_scrapy_civic.py \
  --spider permits \
  --doc-type financial \
  --url "https://example.gov/DocumentCenter/Index/456"
```

### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--spider` | Spider type: agenda, bids, services, permits | agenda |
| `--url` | Target URL to scrape | Required |
| `--doc-type` | Document type for permits spider | permit |
| `--limit` | Max items to scrape (0=unlimited) | 0 |
| `--delay` | Download delay in seconds | Spider default |
| `--concurrent` | Concurrent requests | Spider default |
| `--dry-run` | Preview settings without running | false |

### Rate Limiting

Built-in Scrapy settings ensure polite scraping:

| Spider | Delay | Concurrent | Notes |
|--------|-------|------------|-------|
| AgendaCenter | 10s + random | 1 | Most conservative |
| Others | 2s + random | 4 | Moderate |

AutoThrottle automatically increases delay if server is slow.

## Pipeline

`StructureItPipeline` (`src/structure_it/scrapers/civic_plus/pipelines.py`)

1. **Head Check**: Validates file size before download (max 100MB)
2. **Smart Unwrapping**: Detects viewer pages, extracts real download links
3. **Content Conversion**: PDF/HTML to Markdown via MarkItDown
4. **CDC Check**: Skips unchanged documents (content hash)
5. **Extraction**: Gemini with domain-specific schema
6. **Storage**: DuckDB + JSON

## Future Work

- RSS Spider for CivicNotice (Public Notices)
- Deep PDF table extraction for Budget documents
- Media transcript integration for audio/video links
