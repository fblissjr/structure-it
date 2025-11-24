"""Configuration for structure-it.

Centralized configuration for model defaults and other settings.
Uses environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


# Model Configuration
DEFAULT_MODEL = os.getenv("STRUCTURE_IT_MODEL", "gemini-2.5-flash")
"""Default Gemini model for all extractors and generators.

Can be overridden via STRUCTURE_IT_MODEL environment variable.
Common models:
- gemini-2.5-flash (default, fast and cost-effective)
- gemini-2.0-flash-exp (experimental features)
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
