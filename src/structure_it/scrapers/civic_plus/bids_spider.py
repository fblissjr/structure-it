"""Spider for scraping Bids and RFPs from CivicPlus."""

import re
from datetime import datetime
from urllib.parse import urljoin

import scrapy

from structure_it.config import get_scraper_settings


class CivicPlusBidsSpider(scrapy.Spider):
    """Spider for scraping Bids/RFPs from CivicPlus Bids.aspx."""

    name = "civic_plus_bids"

    # Use moderate profile for secondary data sources
    custom_settings = get_scraper_settings("moderate")

    def __init__(self, place_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Default to a common Bids URL pattern if not provided
        self.start_url = place_url if place_url else "https://example.com/Bids.aspx"
        self.start_urls = [self.start_url]

    def parse(self, response):
        """Parse the main Bids list page."""
        # Logic: Find the main table of bids
        # CivicPlus usually has a table with class "bid-row" or similar structure
        
        # Try to find rows. The roadmap suggests tr.bid-row
        rows = response.css("tr.bid-row")
        
        # Fallback: generic table rows in a main container
        if not rows:
            rows = response.css("table#bidsTable tbody tr, table.bids-table tbody tr")

        for row in rows:
            # Extract basic info from the row to pass as meta
            title_link = row.css("a.bid-title, td.title a")
            if not title_link:
                # Fallback: find any link in the first couple of cells
                title_link = row.css("td:nth-child(1) a, td:nth-child(2) a")
            
            if not title_link:
                continue

            href = title_link.attrib["href"]
            full_url = urljoin(response.url, href)
            title = title_link.css("::text").get().strip()
            
            status = row.css("span.status::text, td.status::text").get()
            if status:
                status = status.strip()

            yield scrapy.Request(
                url=full_url,
                callback=self.parse_bid_detail,
                meta={
                    "title": title,
                    "status": status,
                    "source_type": "civic_bid"
                }
            )

    def parse_bid_detail(self, response):
        """Parse the Bid Detail page."""
        
        # Extract metadata from the detail page
        # We let Gemini do most of the heavy lifting from the HTML text, 
        # but we guide it with what we found.

        # Find related documents
        # Roadmap: div#relatedDocuments a
        doc_links = response.css("div#relatedDocuments a, div.related-documents a")
        documents = []
        for link in doc_links:
            doc_href = link.attrib.get("href")
            if doc_href:
                documents.append(urljoin(response.url, doc_href))

        # We yield the Page itself as the item to be processed
        yield {
            "source_type": "civic_bid",
            "title": response.meta["title"],
            "status": response.meta.get("status"),
            "url": response.url,
            "documents": documents,
            "scraped_at": datetime.now().isoformat(),
            "content_type": "html" # Hint for pipeline
        }
