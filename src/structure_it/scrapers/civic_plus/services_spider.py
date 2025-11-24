"""Spider for scraping Service Requests (Request Tracker) from CivicPlus."""

import re
from datetime import datetime
from urllib.parse import urljoin

import scrapy


class CivicPlusServicesSpider(scrapy.Spider):
    """Spider for scraping Service Requests from CivicPlus RequestTracker.aspx."""

    name = "civic_plus_services"

    custom_settings = {
        "CONCURRENT_REQUESTS": 4,
        "DOWNLOAD_DELAY": 2.0,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 2.0,
        "AUTOTHROTTLE_MAX_DELAY": 60.0,
        "USER_AGENT": "CivicDataBot/1.0 (+https://github.com/fredbliss/structure-it)",
    }

    def __init__(self, place_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_url = place_url if place_url else "https://example.com/RequestTracker.aspx"
        self.start_urls = [self.start_url]

    def parse(self, response):
        """Parse the Request Tracker page."""
        # Logic: Find the list of recent requests
        # Roadmap suggests .req-list .req-item
        
        items = response.css(".req-list .req-item, div.request-item")
        
        # If list is empty, check for table structure
        if not items:
             items = response.css("table.request-table tr")

        for item in items:
            # Extract basic info
            # Often these are not links to full pages but just rows of data
            # So we might need to construct the text content here
            
            # Try to find a link if it exists
            link = item.css("a::attr(href)").get()
            full_url = urljoin(response.url, link) if link else response.url
            
            text_content = item.css("::text").getall()
            text_content = " ".join([t.strip() for t in text_content if t.strip()])
            
            # Identify ID
            # Often like "Request #12345"
            request_id = None
            match = re.search(r"Request\s*[#:]?\s*(\d+)", text_content, re.IGNORECASE)
            if match:
                request_id = match.group(1)
                # If we have an ID but no specific URL, maybe we can construct one or make the ID the unique key
                if full_url == response.url:
                    full_url = f"{response.url}#id={request_id}"

            yield {
                "source_type": "civic_service_request",
                "url": full_url,
                "title": f"Service Request {request_id}" if request_id else "Unknown Request",
                "raw_text": text_content, # Pass raw text for extractor if needed
                "scraped_at": datetime.now().isoformat(),
                "content_type": "html_snippet" # Hint for pipeline
            }
