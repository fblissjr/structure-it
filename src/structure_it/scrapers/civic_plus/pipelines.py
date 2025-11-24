"""Scrapy Pipelines for structure-it.

This pipeline integrates Scrapy with our StarSchemaStorage and GeminiExtractor.
"""

import asyncio
from pathlib import Path
from urllib.parse import urljoin

from markitdown import MarkItDown
from parsel import Selector

from structure_it.extractors import GeminiExtractor
from structure_it.schemas.civic import (
    CivicMeeting, 
    BuildingPermit, 
    CivicBid, 
    CivicServiceRequest, 
    CivicFinancialReport
)
from structure_it.storage.star_schema_storage import StarSchemaStorage
from structure_it.utils.hashing import generate_entity_id, generate_id
from structure_it.utils.safety import DEFAULT_SAFE_SESSION


class StructureItPipeline:
    """Pipeline to download, extract, and store civic data.
    
    Leverages Scrapy's native async support.
    """

    def __init__(self):
        self.storage = StarSchemaStorage()
        self.md = MarkItDown()
        self.meeting_extractor = GeminiExtractor(schema=CivicMeeting)
        self.permit_extractor = GeminiExtractor(schema=BuildingPermit)
        self.bid_extractor = GeminiExtractor(schema=CivicBid)
        self.service_extractor = GeminiExtractor(schema=CivicServiceRequest)
        self.financial_extractor = GeminiExtractor(schema=CivicFinancialReport)
        self.session = DEFAULT_SAFE_SESSION

    async def process_item(self, item, spider):
        """Process a single item asynchronously."""
        url = item["url"]
        source_type = item.get("source_type", "civic_meeting")
        entity_id = generate_entity_id(url, source_type)

        spider.logger.info(f"Processing item: {item.get('title', 'Untitled')} ({url})")

        # Determine extension and expected type
        ext = ".pdf"
        expected_html = False
        if item.get("content_type") == "html" or item.get("content_type") == "html_snippet" or url.endswith(".aspx") or url.endswith(".html"):
            ext = ".html"
            expected_html = True
        
        # Download to temp (Ingestion Phase)
        temp_path = Path(f"temp_downloads/{entity_id}{ext}")
        temp_path.parent.mkdir(exist_ok=True)

        try:
            # 1. Download / Prepare Content
            content = ""
            if item.get("content_type") == "html_snippet" and item.get("raw_text"):
                # Special case: We already scraped the text
                content = item["raw_text"]
                # No need to download or convert
            else:
                # Run in thread if needed, but requests is blocking.
                if not temp_path.exists():
                    spider.logger.info(f"Downloading {url}...")
                    # Pass expected_html flag to handle viewer unwrapping
                    await asyncio.to_thread(self._download_file, url, temp_path, expected_html)

                # 2. Convert (CPU Bound - Run in Thread)
                spider.logger.info("Converting to MD...")
                result = await asyncio.to_thread(self.md.convert, str(temp_path))
                content = result.text_content

            # 3. CDC Check (Memory Phase)
            content_hash = generate_id(content)
            
            is_new, has_changed = await asyncio.to_thread(
                self.storage.check_document_status, entity_id, content_hash
            )

            if not is_new and not has_changed:
                spider.logger.info(f"Skipping {entity_id} (No Change)")
                return item

            # 4. Extraction (Brain Phase - Network Bound)
            spider.logger.info(f"Extracting with Gemini ({source_type})...")
            
            if source_type == "building_permit":
                prompt = f"Extract building permit data from this document: {item.get('title')}"
                extracted_data = await self.permit_extractor.extract(content=content, prompt=prompt)
                extracted_data.source_url = url
                
            elif source_type == "civic_bid":
                prompt = f"Extract bid/RFP data from this page. Title: {item.get('title')}. Status: {item.get('status')}"
                extracted_data = await self.bid_extractor.extract(content=content, prompt=prompt)
                extracted_data.source_url = url
                extracted_data.documents = item.get("documents", [])
                if item.get("status"):
                    extracted_data.status = item["status"]

            elif source_type == "civic_service_request":
                prompt = f"Extract service request data from this entry: {item.get('title')}"
                extracted_data = await self.service_extractor.extract(content=content, prompt=prompt)
                extracted_data.source_url = url

            elif source_type == "civic_financial_report":
                prompt = f"Extract financial report data from this document: {item.get('title')}"
                extracted_data = await self.financial_extractor.extract(content=content, prompt=prompt)
                extracted_data.source_url = url

            else:
                # Default to meeting
                prompt = f"Extract meeting data for {item.get('committee_name')} {item.get('asset_type')} dated {item.get('meeting_date')}"
                extracted_data = await self.meeting_extractor.extract(content=content, prompt=prompt)
                
                extracted_data.source_url = url
                extracted_data.document_type = item.get("asset_type", "Other")
                extracted_data.government_body = item.get("committee_name", "Unknown")
                if hasattr(extracted_data, 'date') and item.get('meeting_date'):
                     extracted_data.date = item['meeting_date']

            # 5. Storage
            await self.storage.store_entity(
                entity_id=entity_id,
                source_type=source_type,
                source_url=url,
                raw_content=content,
                structured_data=extracted_data.to_dict(),
                metadata=item,
            )
            spider.logger.info(f"Successfully stored {entity_id}")

        except Exception as e:
            spider.logger.error(f"Error processing {url}: {e}")

        return item

    def _download_file(self, url, path, expected_html=False):
        """Helper for blocking download with viewer unwrapping."""
        
        # 1. HEAD Check for size and type
        try:
            head = self.session.head(url, allow_redirects=True, timeout=5)
            size = int(head.headers.get('Content-Length', 0))
            content_type = head.headers.get('Content-Type', '').lower()
            
            if size > 100_000_000: # 100MB limit
                raise ValueError(f"File too large: {size} bytes")
            
            # 2. Viewer Page Detection
            if "text/html" in content_type and not expected_html:
                # We expected a binary file (PDF), but got HTML.
                # This might be a viewer wrapper.
                print(f"Detected HTML wrapper for expected binary: {url}. Attempting to unwrap...")
                
                # Fetch the HTML
                r = self.session.get(url, timeout=10)
                r.raise_for_status()
                html_content = r.text
                
                # Use Selector to find a better link
                sel = Selector(text=html_content)
                
                # Common CivicPlus download patterns
                # 1. <a id="download-link" ...>
                # 2. <a href=".../View/...?write=true">
                # 3. Link with text "Download"
                
                download_url = None
                
                # Try specific ID first
                download_url = sel.css("#download-link::attr(href)").get()
                
                if not download_url:
                    # Try link with 'write=true' (CivicPlus standard for forcing download)
                    download_url = sel.css('a[href*="write=true"]::attr(href)').get()
                    
                if not download_url:
                    # Try link with text "Download"
                    # xpath: //a[contains(text(), "Download")]
                    download_url = sel.xpath('//a[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "download")]/@href').get()

                if download_url:
                    # Resolve relative URL
                    download_url = urljoin(url, download_url)
                    print(f"Found unwrapped download URL: {download_url}")
                    # Recursively call (but ensure we don't loop forever - simple recursion is okay here as likely 1 level)
                    # We pass expected_html=False again to ensure the new link is also binary
                    return self._download_file(download_url, path, expected_html=False)
                else:
                    print(f"Could not find download link in wrapper. Proceeding with HTML content.")
                    # Write the HTML content we already fetched? 
                    # Or just let it fall through? 
                    # If we write HTML to a .pdf file, MarkItDown might fail or just extract text.
                    # Let's write the HTML content we have to the path to avoid re-requesting
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(html_content)
                    return

        except Exception as e:
            # If head fails or isn't supported, we proceed with caution
            # print(f"Head request failed: {e}")
            pass

        # 3. Normal Download
        with self.session.get(url, stream=True) as r:
            r.raise_for_status()
            with open(path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
