"""Runner script for Scrapy spiders."""

import argparse
import os
from scrapy.crawler import CrawlerProcess
from structure_it.scrapers.civic_plus.spider import CivicPlusSpider
from structure_it.scrapers.civic_plus.permits_spider import CivicPlusPermitsSpider
from structure_it.scrapers.civic_plus.bids_spider import CivicPlusBidsSpider
from structure_it.scrapers.civic_plus.services_spider import CivicPlusServicesSpider
from structure_it.config import GOOGLE_API_KEY

def run_scraper(target_url, spider_type="agenda", **kwargs):
    """Run the CivicPlus scraper."""
    
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not set.")
        return

    # Scrapy Settings
    settings = {
        'ITEM_PIPELINES': {
            'structure_it.scrapers.civic_plus.pipelines.StructureItPipeline': 300,
        },
        'LOG_LEVEL': 'INFO',
        # Limit for testing purposes
        'CLOSESPIDER_ITEMCOUNT': 10
    }
    
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
    parser = argparse.ArgumentParser(description="Run CivicPlus scrapers.")
    parser.add_argument("--url", help="Target URL (AgendaCenter, DocumentCenter folder, Bids.aspx, etc)")
    parser.add_argument("--spider", choices=["agenda", "permits", "bids", "services"], default="agenda", help="Which spider to run")
    parser.add_argument("--doc-type", default="permit", help="Document type for permits/document center spider (e.g. 'permit', 'financial')")
    
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
        
    run_scraper(target_url, args.spider, doc_type=args.doc_type)