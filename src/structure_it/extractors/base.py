"""Base extractor interface for structured data extraction."""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

TSchema = TypeVar("TSchema", bound=BaseModel)


class BaseExtractor(ABC, Generic[TSchema]):
    """Abstract base class for structured data extractors.

    Extractors take unstructured input (text, images, documents) and produce
    structured output conforming to a Pydantic schema.

    Type Parameters:
        TSchema: The Pydantic schema type for structured output.
    """

    def __init__(self, schema: type[TSchema]) -> None:
        """Initialize the extractor with a schema.

        Args:
            schema: Pydantic model class defining the output structure.
        """
        self.schema = schema

    @abstractmethod
    async def extract(
        self,
        content: str | bytes,
        prompt: str | None = None,
        **kwargs: Any,
    ) -> TSchema:
        """Extract structured data from unstructured content.

        Args:
            content: Unstructured input content (text, image bytes, etc.).
            prompt: Optional instruction prompt for the extraction.
            **kwargs: Additional provider-specific parameters.

        Returns:
            Structured output conforming to the schema.

        Raises:
            ExtractionError: If extraction fails.
        """
        pass

    @abstractmethod
    async def extract_batch(
        self,
        contents: list[str | bytes],
        prompt: str | None = None,
        **kwargs: Any,
    ) -> list[TSchema]:
        """Extract structured data from multiple contents.

        Args:
            contents: List of unstructured inputs.
            prompt: Optional instruction prompt for the extraction.
            **kwargs: Additional provider-specific parameters.

        Returns:
            List of structured outputs conforming to the schema.

        Raises:
            ExtractionError: If extraction fails.
        """
        pass


class ExtractionError(Exception):
    """Exception raised when extraction fails."""

    pass
