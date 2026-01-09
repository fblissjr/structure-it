"""Runner script for Scrapy spiders with ELT support.

ELT Modes:
    --mode extract   : Spider only -> data/raw/ (Bronze)
    --mode transform : data/raw/ -> data/staged/ (Silver) with Gemini
    --mode load      : data/staged/ -> DuckDB (Gold)
    --mode elt       : Run all three stages sequentially
    --mode full      : Legacy single-pass ETL (default)

Usage:
    # ELT workflow (recommended)
    uv run python examples/run_scrapy_civic.py --mode extract --spider agenda --url URL --limit 5
    uv run python examples/run_scrapy_civic.py --mode transform
    uv run python examples/run_scrapy_civic.py --mode load

    # Or run full ELT in one command
    uv run python examples/run_scrapy_civic.py --mode elt --spider agenda --url URL --limit 5

    # Legacy single-pass (backwards compatible)
    uv run python examples/run_scrapy_civic.py --spider agenda --url URL --limit 5
"""

import argparse
import asyncio
import os
from pathlib import Path

from scrapy.crawler import CrawlerProcess

from structure_it.config import GOOGLE_API_KEY
from structure_it.scrapers.civic_plus.bids_spider import CivicPlusBidsSpider
from structure_it.scrapers.civic_plus.permits_spider import CivicPlusPermitsSpider
from structure_it.scrapers.civic_plus.services_spider import CivicPlusServicesSpider
from structure_it.scrapers.civic_plus.spider import CivicPlusSpider


def run_extract(target_url, spider_type="agenda", **kwargs):
    """Run spider and save to raw/ (Bronze layer)."""

    # Use RawStagingPipeline instead of full pipeline
    settings = {
        "ITEM_PIPELINES": {
            "structure_it.scrapers.civic_plus.staging_pipeline.RawStagingPipeline": 300,
        },
        "LOG_LEVEL": kwargs.get("log_level", "INFO"),
    }

    # Apply limits
    limit = kwargs.get("limit", 0)
    if limit > 0:
        settings["CLOSESPIDER_ITEMCOUNT"] = limit

    delay = kwargs.get("delay")
    if delay is not None:
        settings["DOWNLOAD_DELAY"] = delay

    concurrent = kwargs.get("concurrent")
    if concurrent is not None:
        settings["CONCURRENT_REQUESTS"] = concurrent

    process = CrawlerProcess(settings)

    print("=" * 60)
    print("EXTRACT: Source -> data/raw/ (Bronze)")
    print("=" * 60)

    if spider_type == "permits":
        doc_type = kwargs.get("doc_type", "permit")
        print(f"Spider: permits | URL: {target_url} | Type: {doc_type}")
        process.crawl(CivicPlusPermitsSpider, start_url=target_url, doc_type=doc_type)
    elif spider_type == "bids":
        print(f"Spider: bids | URL: {target_url}")
        process.crawl(CivicPlusBidsSpider, place_url=target_url)
    elif spider_type == "services":
        print(f"Spider: services | URL: {target_url}")
        process.crawl(CivicPlusServicesSpider, place_url=target_url)
    else:
        print(f"Spider: agenda | URL: {target_url}")
        process.crawl(CivicPlusSpider, place_url=target_url)

    print()
    process.start()


def run_transform(**kwargs):
    """Transform raw/ to staged/ (Silver layer)."""
    from structure_it.etl.transform import transform_all

    print("=" * 60)
    print("TRANSFORM: data/raw/ -> data/staged/ (Silver)")
    print("=" * 60)

    raw_dir = Path(kwargs.get("raw_dir", "./data/raw"))
    staged_dir = Path(kwargs.get("staged_dir", "./data/staged"))
    force = kwargs.get("force", False)

    transformed, skipped, failed = asyncio.run(
        transform_all(raw_dir, staged_dir, force=force)
    )

    print()
    print(f"Transformed: {transformed} | Skipped: {skipped} | Failed: {failed}")


def run_load(**kwargs):
    """Load staged/ to DuckDB (Gold layer)."""
    from structure_it.etl.load import load_all

    print("=" * 60)
    print("LOAD: data/staged/ -> DuckDB (Gold)")
    print("=" * 60)

    staged_dir = Path(kwargs.get("staged_dir", "./data/staged"))
    db_path = Path(kwargs.get("db_path", "./data/structure_it.duckdb"))
    force = kwargs.get("force", False)

    counts = asyncio.run(load_all(staged_dir, db_path, force=force))

    print()
    print(f"Created: {counts['created']} | Updated: {counts['updated']} | Unchanged: {counts['unchanged']} | Errors: {counts['error']}")


def run_scraper(target_url, spider_type="agenda", dry_run=False, **kwargs):
    """Run the CivicPlus scraper (legacy full ETL mode)."""

    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not set.")
        return

    # Base Scrapy Settings
    settings = {
        "ITEM_PIPELINES": {
            "structure_it.scrapers.civic_plus.pipelines.StructureItPipeline": 300,
        },
        "LOG_LEVEL": kwargs.get("log_level", "INFO"),
    }

    # Apply optional CLI overrides
    limit = kwargs.get("limit", 0)
    if limit > 0:
        settings["CLOSESPIDER_ITEMCOUNT"] = limit

    delay = kwargs.get("delay")
    if delay is not None:
        settings["DOWNLOAD_DELAY"] = delay

    concurrent = kwargs.get("concurrent")
    if concurrent is not None:
        settings["CONCURRENT_REQUESTS"] = concurrent

    # Dry run mode - show settings and exit
    if dry_run:
        print("=" * 60)
        print("DRY RUN - Settings Preview (not executing)")
        print("=" * 60)
        print(f"Spider:     {spider_type}")
        print(f"Target URL: {target_url}")
        print(f"Doc Type:   {kwargs.get('doc_type', 'N/A')}")
        print("-" * 60)
        print("Scrapy Settings:")
        for key, value in sorted(settings.items()):
            print(f"  {key}: {value}")
        print("-" * 60)
        print("Spider Defaults (if not overridden):")
        if spider_type == "agenda":
            print("  DOWNLOAD_DELAY: 10.0 (conservative)")
            print("  CONCURRENT_REQUESTS: 1")
            print("  AUTOTHROTTLE_ENABLED: True")
        else:
            print("  DOWNLOAD_DELAY: 2.0")
            print("  CONCURRENT_REQUESTS: 4")
            print("  AUTOTHROTTLE_ENABLED: True")
        print("=" * 60)
        return

    process = CrawlerProcess(settings)

    if spider_type == "permits":
        doc_type = kwargs.get("doc_type", "permit")
        print(f"Starting Document Center Spider for {target_url} (Type: {doc_type})...")
        process.crawl(CivicPlusPermitsSpider, start_url=target_url, doc_type=doc_type)
    elif spider_type == "bids":
        print(f"Starting Bids Spider for {target_url}...")
        process.crawl(CivicPlusBidsSpider, place_url=target_url)
    elif spider_type == "services":
        print(f"Starting Services Spider for {target_url}...")
        process.crawl(CivicPlusServicesSpider, place_url=target_url)
    else:
        print(f"Starting Agenda Spider for {target_url}...")
        process.crawl(CivicPlusSpider, place_url=target_url)

    process.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run CivicPlus scrapers with ELT support.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ELT Workflow (recommended):
  # Step 1: Extract to raw/
  uv run python examples/run_scrapy_civic.py --mode extract --spider agenda --url URL --limit 5

  # Step 2: Transform to staged/
  uv run python examples/run_scrapy_civic.py --mode transform

  # Step 3: Load to DuckDB
  uv run python examples/run_scrapy_civic.py --mode load

  # Or run all three in sequence
  uv run python examples/run_scrapy_civic.py --mode elt --spider agenda --url URL --limit 5

Legacy Mode (backwards compatible):
  uv run python examples/run_scrapy_civic.py --spider agenda --url URL --limit 1
        """,
    )
    parser.add_argument(
        "--mode",
        choices=["extract", "transform", "load", "elt", "full"],
        default="full",
        help="ELT mode: extract|transform|load|elt|full (default: full)",
    )
    parser.add_argument(
        "--url", help="Target URL (AgendaCenter, DocumentCenter folder, Bids.aspx, etc)"
    )
    parser.add_argument(
        "--spider",
        choices=["agenda", "permits", "bids", "services"],
        default="agenda",
        help="Which spider to run (default: agenda)",
    )
    parser.add_argument(
        "--doc-type",
        default="permit",
        help="Document type for permits spider: 'permit' or 'financial' (default: permit)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Max items to scrape, 0=unlimited (default: 0)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=None,
        help="Download delay in seconds (overrides spider default)",
    )
    parser.add_argument(
        "--concurrent",
        type=int,
        default=None,
        help="Concurrent requests (overrides spider default)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview settings without running the scraper",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Scrapy log level (default: INFO)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-transform/re-load even if unchanged",
    )

    args = parser.parse_args()

    # Build kwargs for all modes
    kwargs = {
        "doc_type": args.doc_type,
        "limit": args.limit,
        "delay": args.delay,
        "concurrent": args.concurrent,
        "log_level": args.log_level,
        "force": args.force,
    }

    # Handle different modes
    if args.mode == "transform":
        run_transform(**kwargs)

    elif args.mode == "load":
        run_load(**kwargs)

    elif args.mode == "extract":
        target_url = args.url or os.getenv("CIVIC_PLUS_URL")
        if not target_url:
            print("Error: --url required for extract mode")
            exit(1)
        run_extract(target_url, args.spider, **kwargs)

    elif args.mode == "elt":
        # Run all three stages
        target_url = args.url or os.getenv("CIVIC_PLUS_URL")
        if not target_url:
            print("Error: --url required for elt mode")
            exit(1)

        print("Running full ELT pipeline...")
        print()
        run_extract(target_url, args.spider, **kwargs)
        print()
        run_transform(**kwargs)
        print()
        run_load(**kwargs)

    else:
        # Legacy full mode (default)
        target_url = args.url or os.getenv("CIVIC_PLUS_URL")

        if not target_url:
            if args.spider == "permits":
                target_url = "https://example.com/DocumentCenter/Index/123"
            elif args.spider == "bids":
                target_url = "https://example.com/Bids.aspx"
            elif args.spider == "services":
                target_url = "https://example.com/RequestTracker.aspx"
            else:
                target_url = "https://example.com/AgendaCenter"
            print(f"Warning: No URL provided. Using example: {target_url}")

        run_scraper(
            target_url,
            args.spider,
            dry_run=args.dry_run,
            **kwargs,
        )
