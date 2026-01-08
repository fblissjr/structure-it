"""Configuration for structure-it.

Centralized configuration for model defaults and other settings.
Uses environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


# Model Configuration
DEFAULT_MODEL = os.getenv("STRUCTURE_IT_MODEL", "gemini-3-flash-preview")
"""Default Gemini model for all extractors and generators.

Can be overridden via STRUCTURE_IT_MODEL environment variable.
Common models:
- gemini-3-flash-preview (default, latest preview)
- gemini-2.5-flash (stable, fast and cost-effective)
- gemini-2.5-pro (highest quality, slower)
"""

# Generation Configuration
DEFAULT_TEMPERATURE = float(os.getenv("STRUCTURE_IT_TEMPERATURE", "0.8"))
"""Default temperature for generation tasks (0.0 = deterministic, 1.0 = creative)."""

# Storage Configuration
DEFAULT_DB_PATH = os.getenv("STRUCTURE_IT_DB_PATH", "./data/structure_it.duckdb")
"""Default path for DuckDB storage."""

DEFAULT_JSON_PATH = os.getenv("STRUCTURE_IT_JSON_PATH", "./data/entities")
"""Default base path for JSON storage."""

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
"""Google API key for Gemini access (required)."""

# =============================================================================
# Scraper Configuration
# =============================================================================

SCRAPER_USER_AGENT = os.getenv(
    "STRUCTURE_IT_USER_AGENT",
    "CivicDataBot/1.0 (+https://github.com/fredbliss/structure-it)"
)
"""User agent for all scrapers."""

# AutoThrottle settings (shared across all scrapers)
SCRAPER_AUTOTHROTTLE_ENABLED = os.getenv("STRUCTURE_IT_AUTOTHROTTLE", "true").lower() == "true"
SCRAPER_AUTOTHROTTLE_START = float(os.getenv("STRUCTURE_IT_AUTOTHROTTLE_START", "2.0"))
SCRAPER_AUTOTHROTTLE_MAX = float(os.getenv("STRUCTURE_IT_AUTOTHROTTLE_MAX", "60.0"))

# Randomize delay (adds jitter: 0.5x to 1.5x configured delay)
SCRAPER_RANDOMIZE_DELAY = os.getenv("STRUCTURE_IT_RANDOMIZE_DELAY", "true").lower() == "true"

# Conservative profile (for primary data like AgendaCenter)
SCRAPER_CONSERVATIVE_CONCURRENT = int(os.getenv("STRUCTURE_IT_SCRAPER_CONCURRENT_CONSERVATIVE", "1"))
SCRAPER_CONSERVATIVE_DELAY = float(os.getenv("STRUCTURE_IT_SCRAPER_DELAY_CONSERVATIVE", "10.0"))

# Moderate profile (for secondary data like Bids, Permits, Services)
SCRAPER_MODERATE_CONCURRENT = int(os.getenv("STRUCTURE_IT_SCRAPER_CONCURRENT_MODERATE", "4"))
SCRAPER_MODERATE_DELAY = float(os.getenv("STRUCTURE_IT_SCRAPER_DELAY_MODERATE", "2.0"))


def get_scraper_settings(profile: str = "moderate") -> dict:
    """Get Scrapy settings dict for a scraper profile.

    Args:
        profile: 'conservative' for primary sources (slower, safer)
                 'moderate' for secondary sources (faster)

    Returns:
        Dict of Scrapy settings.
    """
    if profile == "conservative":
        concurrent = SCRAPER_CONSERVATIVE_CONCURRENT
        delay = SCRAPER_CONSERVATIVE_DELAY
        target_concurrency = 1.0
    else:  # moderate
        concurrent = SCRAPER_MODERATE_CONCURRENT
        delay = SCRAPER_MODERATE_DELAY
        target_concurrency = float(concurrent)

    return {
        "CONCURRENT_REQUESTS": concurrent,
        "DOWNLOAD_DELAY": delay,
        "RANDOMIZE_DOWNLOAD_DELAY": SCRAPER_RANDOMIZE_DELAY,
        "AUTOTHROTTLE_ENABLED": SCRAPER_AUTOTHROTTLE_ENABLED,
        "AUTOTHROTTLE_START_DELAY": SCRAPER_AUTOTHROTTLE_START,
        "AUTOTHROTTLE_MAX_DELAY": SCRAPER_AUTOTHROTTLE_MAX,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": target_concurrency,
        "USER_AGENT": SCRAPER_USER_AGENT,
        "HTTPCACHE_ENABLED": False,
    }
