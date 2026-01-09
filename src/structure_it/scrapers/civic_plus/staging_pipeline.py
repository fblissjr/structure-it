"""Raw Staging Pipeline for ELT architecture (Bronze Layer).

This pipeline stages raw data from source systems:
- Downloads files via Scrapy (rate-limited)
- Saves original files untouched to data/raw/
- Saves minimal source metadata

NO transformation happens here - that's the Transform step.

ELT Layers:
- Raw (Bronze): data/raw/ - this pipeline
- Staged (Silver): data/staged/ - transform_staged.py
- Final (Gold): DuckDB - load_staged.py
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

from structure_it.utils.hashing import generate_entity_id


class RawStagingPipeline:
    """Pipeline that stages raw source data (Bronze layer).

    Only saves:
    - Original downloaded file (untouched)
    - Source metadata (URL, timestamps, scrape context)

    No markdown conversion, no Gemini extraction.
    """

    def __init__(self, raw_dir: str = "./data/raw"):
        self.raw_dir = Path(raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    async def process_item(self, item, spider):
        """Stage raw item from source system.

        Creates folder structure:
        data/raw/{source_type}/{entity_id}/
            - original.{pdf|html}   # Untouched source file
            - source.json           # Minimal source metadata
        """
        url = item["url"]
        source_type = item.get("source_type", "civic_meeting")
        entity_id = generate_entity_id(url, source_type)

        # Create raw staging folder
        item_dir = self.raw_dir / source_type / entity_id
        item_dir.mkdir(parents=True, exist_ok=True)

        spider.logger.info(f"[RAW] Staging: {item.get('title', 'Untitled')} -> {item_dir}")

        try:
            # 1. Copy original file (untouched)
            original_path = None
            if item.get("temp_path"):
                temp_path = Path(item["temp_path"])
                if temp_path.exists():
                    ext = temp_path.suffix or ".pdf"
                    original_path = item_dir / f"original{ext}"
                    shutil.copy2(temp_path, original_path)
                    spider.logger.info(f"[RAW] Saved original: {original_path.name}")

            # 2. Save source metadata (minimal - just what came from source)
            source_metadata = {
                "entity_id": entity_id,
                "source_type": source_type,
                "url": url,
                "title": item.get("title", ""),
                "original_file": original_path.name if original_path else None,
                # Source context
                "committee_name": item.get("committee_name"),
                "meeting_date": item.get("meeting_date"),
                "asset_type": item.get("asset_type"),
                "content_type": item.get("content_type"),
                # Timestamps
                "scraped_at": item.get("scraped_at", datetime.now().isoformat()),
                "raw_staged_at": datetime.now().isoformat(),
            }

            # Add any extra source fields
            for key in ["status", "documents", "doc_type"]:
                if key in item:
                    source_metadata[key] = item[key]

            source_path = item_dir / "source.json"
            source_path.write_text(
                json.dumps(source_metadata, indent=2, default=str),
                encoding="utf-8"
            )

            spider.logger.info(f"[RAW] Staged {entity_id}")

        except Exception as e:
            spider.logger.error(f"[RAW] Error staging {url}: {e}")

        return item
