"""Runner script for Scrapy spiders.

Usage:
    uv run python examples/run_scrapy_civic.py --spider agenda --url URL
    uv run python examples/run_scrapy_civic.py --spider agenda --url URL --limit 5
    uv run python examples/run_scrapy_civic.py --spider agenda --url URL --dry-run
"""

import argparse
import os

from scrapy.crawler import CrawlerProcess

from structure_it.config import GOOGLE_API_KEY
from structure_it.scrapers.civic_plus.bids_spider import CivicPlusBidsSpider
from structure_it.scrapers.civic_plus.permits_spider import CivicPlusPermitsSpider
from structure_it.scrapers.civic_plus.services_spider import CivicPlusServicesSpider
from structure_it.scrapers.civic_plus.spider import CivicPlusSpider


def run_scraper(target_url, spider_type="agenda", dry_run=False, **kwargs):
    """Run the CivicPlus scraper."""

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
        description="Run CivicPlus scrapers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Safe test run (1 item)
  uv run python examples/run_scrapy_civic.py --spider agenda --url URL --limit 1

  # Production run (full scrape, defaults)
  uv run python examples/run_scrapy_civic.py --spider agenda --url URL

  # Custom throttling
  uv run python examples/run_scrapy_civic.py --spider agenda --url URL --delay 15 --concurrent 1

  # Preview settings without running
  uv run python examples/run_scrapy_civic.py --spider agenda --url URL --dry-run
        """,
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

    args = parser.parse_args()

    # Default to generic example or environment variable
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
        doc_type=args.doc_type,
        limit=args.limit,
        delay=args.delay,
        concurrent=args.concurrent,
        log_level=args.log_level,
    )
