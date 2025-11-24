import asyncio
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path

from civic_scraper.platforms import CivicPlusSite
from markitdown import MarkItDown

from structure_it.config import GOOGLE_API_KEY
from structure_it.extractors import GeminiExtractor
from structure_it.extractors.civic_patch import patch_civic_scraper
from structure_it.schemas.civic import CivicMeeting
from structure_it.storage.star_schema_storage import StarSchemaStorage
from structure_it.utils.hashing import generate_entity_id, generate_id
from structure_it.utils.safety import DEFAULT_SAFE_SESSION

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def process_civic_data(
    place_name: str = "Example Village",
    base_url: str = "https://example.com/AgendaCenter",
    days_back: int = 30
):
    """Collect and process civic data with Gold Standard safety."""

    if not GOOGLE_API_KEY:
        logger.error("GOOGLE_API_KEY not set. Cannot proceed with extraction.")
        return

    # 1. Apply Safety Patch
    # This ensures even the discovery phase (listing files) is polite
    patch_civic_scraper()

    # Initialize storage
    storage = StarSchemaStorage()

    # Initialize scraper
    # Note: We don't use the 'download' feature of civic-scraper to keep control
    site = CivicPlusSite(base_url, place_name=place_name)

    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")

    logger.info(f"Scraping {place_name} from {start_date} to {end_date}")

    # 2. Discovery Phase (Safe)
    # This will now use our rate-limited SafeSession under the hood
    assets = site.scrape(start_date=start_date, end_date=end_date)
    
    logger.info(f"Found {len(assets)} assets.")

    # Initialize MD converter
    md = MarkItDown()

    # Initialize Extractor
    extractor = GeminiExtractor(schema=CivicMeeting)

    # 3. Ingestion Phase (Safe)
    for asset in assets:
        logger.info(f"Processing: {asset.asset_name} ({asset.asset_type})")

        if asset.asset_type not in ["Agenda", "Minutes"]:
            continue

        entity_id = generate_entity_id(asset.url, "civic_meeting")
        
        # Download Setup
        temp_dir = Path("./temp_downloads")
        temp_dir.mkdir(exist_ok=True)
        safe_name = "".join(c for c in asset.asset_name if c.isalnum() or c in (' ', '.', '_')).strip()
        file_path = temp_dir / f"{safe_name}.pdf"

        # Download with SafeSession (Backoff + Rate Limit)
        if not file_path.exists():
            logger.info(f"Downloading {asset.url}...")
            try:
                # Use stream=True with SafeSession
                # SafeSession.get returns a response object we can iterate
                with DEFAULT_SAFE_SESSION.get(asset.url, stream=True) as response:
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
            except Exception as e:
                logger.error(f"Failed to download {asset.url}: {e}")
                continue
        
        try:
            # Convert
            logger.info("Converting to Markdown...")
            result = md.convert(str(file_path))
            content = result.text_content
            
            # 4. CDC Check (Save $$)
            content_hash = generate_id(content)
            is_new, has_changed = storage.check_document_status(entity_id, content_hash)
            
            if not is_new and not has_changed:
                logger.info(f"Skipping {entity_id}: No content changes.")
                # Touch the record to show we saw it? 
                # (Ideally we'd have a 'touch' method, but this is fine for now)
                continue

            # Extract
            logger.info("Extracting structured data (LLM Call)...")
            meeting_data = await extractor.extract(
                content=content,
                prompt=f"Extract structured meeting information from this {asset.asset_type} for {asset.committee_name}."
            )

            # Enhance Metadata
            meeting_data.source_url = asset.url
            meeting_data.document_type = asset.asset_type
            if not meeting_data.government_body:
                meeting_data.government_body = asset.committee_name

            # Store (Handles CDC auditing)
            logger.info(f"Storing entity {entity_id}...")
            await storage.store_entity(
                entity_id=entity_id,
                source_type="civic_meeting",
                source_url=asset.url,
                raw_content=content,
                structured_data=meeting_data.to_dict(),
                metadata={"place": place_name, "committee": asset.committee_name}
            )

        except Exception as e:
            logger.error(f"Failed to process {asset.asset_name}: {e}")

    logger.info("Processing complete.")

if __name__ == "__main__":
    asyncio.run(process_civic_data())
