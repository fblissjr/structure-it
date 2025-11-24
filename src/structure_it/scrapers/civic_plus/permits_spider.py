"""Spider for scraping Building Permits from CivicPlus Document Center."""

import re
from datetime import datetime
from urllib.parse import urljoin

import scrapy


class CivicPlusPermitsSpider(scrapy.Spider):
    """Spider for scraping permits from CivicPlus Document Center folders."""

    name = "civic_plus_permits"

    custom_settings = {
        "CONCURRENT_REQUESTS": 4,
        "DOWNLOAD_DELAY": 2.0,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 2.0,
        "AUTOTHROTTLE_MAX_DELAY": 60.0,
        "USER_AGENT": "CivicDataBot/1.0 (+https://github.com/fredbliss/structure-it)",
    }

    def __init__(self, start_url=None, doc_type="permit", *args, **kwargs):
        """
        Initialize with a starting URL and document type.
        
        Args:
            start_url: The URL of a Document Center folder.
            doc_type: Type of document to scrape ('permit' or 'financial').
        """
        super().__init__(*args, **kwargs)
        self.start_urls = [start_url] if start_url else []
        self.doc_type = doc_type
        
        if not self.start_urls:
            self.logger.warning("No start_url provided. Spider will do nothing.")

    def parse(self, response):
        """Parse a Document Center folder page."""
        # Look for table rows in the file list
        
        rows = response.css("table tbody tr")
        if not rows:
            # Fallback: Try to find any ViewFile links
            links = response.css('a[href^="/DocumentCenter/View/"]')
            for link in links:
                yield from self._yield_file_item(link, response.url)
            return

        for row in rows:
            # Look for the file link
            link = row.css('a[href^="/DocumentCenter/View/"]')
            if link:
                yield from self._yield_file_item(link[0], response.url)

    def _yield_file_item(self, link_selector, referrer):
        href = link_selector.attrib["href"]
        text = link_selector.css("::text").get() or ""
        
        # Filter based on doc_type
        if self.doc_type == "permit":
            if "permit" not in text.lower() and "report" not in text.lower():
                 pass
            source_type = "building_permit"
        elif self.doc_type == "financial":
            # Financials usually have "Budget", "Report", "CAFR"
            source_type = "civic_financial_report"
        else:
            source_type = "civic_document"

        full_url = urljoin(referrer, href)

        yield {
            "source_type": source_type,
            "title": text.strip(),
            "url": full_url,
            "scraped_at": datetime.now().isoformat(),
            "document_type": self.doc_type.capitalize()
        }
