"""
structure-it: Research sandbox for structuring data with LLM-driven pipelines.

This package provides tools for extracting structured data from unstructured sources
using multimodal LLMs (starting with Google Gemini) and experimenting with different
data modeling approaches optimized for LLM context and reuse.
"""

__version__ = "0.1.0"

from structure_it.extractors.base import BaseExtractor
from structure_it.extractors.gemini import GeminiExtractor
from structure_it.schemas.base import BaseSchema
from structure_it.storage.base import BaseStorage, StoredEntity
from structure_it.storage.duckdb_storage import DuckDBStorage
from structure_it.storage.json_storage import JSONStorage

__all__ = [
    "BaseExtractor",
    "GeminiExtractor",
    "BaseSchema",
    "BaseStorage",
    "StoredEntity",
    "JSONStorage",
    "DuckDBStorage",
]
