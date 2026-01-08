"""CivicPlus Scraper using Scrapy.

This is a port of the civic-scraper logic to the Scrapy framework,
providing industry-standard safety, concurrency, and maintainability.
"""

import re
from datetime import datetime
from urllib.parse import urljoin

import scrapy

from structure_it.config import get_scraper_settings


class CivicPlusSpider(scrapy.Spider):
    """Spider for CivicPlus AgendaCenter."""

    name = "civic_plus"

    # Use conservative profile for primary data sources (AgendaCenter)
    custom_settings = get_scraper_settings("conservative")

    def __init__(self, place_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = place_url
        # Default to generic example if not provided
        if not self.base_url:
            self.base_url = "https://example.com/AgendaCenter"

        self.start_urls = [self.base_url]

    def parse(self, response):
        """Parse the main AgendaCenter page."""
        # Logic ported from civic-scraper parser.py
        # 1. Find all committee divs (id starts with "cat")

        # Scrapy CSS selectors are generally cleaner than BS4
        # div[id^="cat"]
        committee_divs = response.css('div[id^="cat"]')

        for div in committee_divs:
            # Extract committee name
            # Header is usually h2 or h3
            header = div.css("h2::text, h3::text").get()
            if not header:
                # Sometimes text is inside a link or span, clean up
                header = "".join(div.css("h2 *::text, h3 *::text").getall())

            committee_name = header.strip() if header else "Unknown Committee"

            # 2. Find all rows in the table body
            rows = div.css("tbody tr")
            for row in rows:
                # Meeting Title
                meeting_title = row.css("p::text").get() or ""
                meeting_title = meeting_title.strip()

                # Meeting ID (often in the name anchor)
                # <a name="_01012023">
                anchor_name = row.css("a::attr(name)").get()

                meeting_date = None
                if anchor_name:
                    # Parse date from anchor: _MMDDYYYY
                    # Regex: _(\d{2})(\d{2})(\d{4})
                    match = re.search(r"_(\d{2})(\d{2})(\d{4})", anchor_name)
                    if match:
                        m, d, y = match.groups()
                        try:
                            meeting_date = datetime(int(y), int(m), int(d)).strftime("%Y-%m-%d")
                        except ValueError:
                            pass

                # 3. Find all document links
                # civic-scraper looks for links starting with /AgendaCenter/ViewFile and no title
                links = row.css('a[href^="/AgendaCenter/ViewFile"]')

                for link in links:
                    href = link.attrib["href"]

                    # Skip "Previous Versions"
                    if "PreviousVersions" in href:
                        continue

                    # Determine asset type (Agenda, Minutes, Packet, Audio, Video) from URL or text
                    # URL structure: /ViewFile/Item/123?fileID=456
                    # civic-scraper uses the 3rd path segment: /ViewFile/[Type]/...

                    asset_type = "Other"
                    lower_href = href.lower()

                    # Precise detection based on URL path segments if possible
                    parts = href.split("/")
                    if len(parts) > 3 and parts[1] == "ViewFile":
                        # e.g., /AgendaCenter/ViewFile/Agenda/...
                        candidate_type = parts[
                            2
                        ]  # Note: href might be relative so parts index varies
                        # If absolute or relative root: /AgendaCenter/ViewFile/Agenda/
                        # Let's rely on string matching which is safer for varied URLs
                        pass

                    if "packet=true" in lower_href or "agenda_packet" in lower_href:
                        asset_type = "AgendaPacket"
                    elif "/agenda/" in lower_href or "agenda" in lower_href:
                        asset_type = "Agenda"
                    elif "/minutes/" in lower_href or "minutes" in lower_href:
                        asset_type = "Minutes"
                    elif "/audio/" in lower_href or "audio" in lower_href:
                        asset_type = "Audio"
                    elif "/video/" in lower_href or "video" in lower_href:
                        asset_type = "Video"
                    elif "/captions/" in lower_href or "captions" in lower_href:
                        asset_type = "Captions"

                    # Fallback: Override if text is explicit and type is still ambiguous
                    link_text = link.css("::text").get() or ""
                    if asset_type == "Other":
                        if "Agenda" in link_text:
                            asset_type = "Agenda"
                        elif "Minutes" in link_text:
                            asset_type = "Minutes"
                        elif "Packet" in link_text:
                            asset_type = "AgendaPacket"

                    full_url = urljoin(self.base_url, href)

                    yield {
                        "source_type": "civic_meeting",
                        "committee_name": committee_name,
                        "meeting_date": meeting_date,
                        "title": meeting_title,
                        "asset_type": asset_type,
                        "url": full_url,
                        "scraped_at": datetime.now().isoformat(),
                    }
