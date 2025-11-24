"""Gemini-based structured data extractor."""

import asyncio
from typing import Any

from google import genai
from google.genai import types
from pydantic import BaseModel

from structure_it.config import DEFAULT_MODEL
from structure_it.extractors.base import BaseExtractor, ExtractionError, TSchema


class GeminiExtractor(BaseExtractor[TSchema]):
    """Structured data extractor using Google Gemini API.

    Uses Gemini's structured output capabilities to extract data conforming
    to a Pydantic schema from unstructured content.
    """

    def __init__(
        self,
        schema: type[TSchema],
        model_name: str | None = None,
        api_key: str | None = None,
        **model_kwargs: Any,
    ) -> None:
        """Initialize the Gemini extractor.

        Args:
            schema: Pydantic model class defining the output structure.
            model_name: Gemini model to use (defaults to config.DEFAULT_MODEL).
            api_key: Google API key (if not set via environment).
            **model_kwargs: Additional model configuration parameters.
        """
        super().__init__(schema)
        self.model_name = model_name or DEFAULT_MODEL
        self.model_kwargs = model_kwargs

        # Initialize Gemini client
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            from structure_it.config import GOOGLE_API_KEY
            if not GOOGLE_API_KEY:
                raise ValueError(
                    "GOOGLE_API_KEY is not set. Please set the GOOGLE_API_KEY "
                    "environment variable or pass it to the extractor."
                )
            self.client = genai.Client(api_key=GOOGLE_API_KEY)

    async def extract(
        self,
        content: str | bytes,
        prompt: str | None = None,
        **kwargs: Any,
    ) -> TSchema:
        """Extract structured data from unstructured content.

        Args:
            content: Unstructured input content (text or image bytes).
            prompt: Optional instruction prompt for the extraction.
            **kwargs: Additional generation parameters (temperature, etc.).

        Returns:
            Structured output conforming to the schema.

        Raises:
            ExtractionError: If extraction fails.
        """
        try:
            # Build the prompt
            instruction = prompt or f"Extract structured data from the content."

            # Prepare content based on type
            if isinstance(content, bytes):
                # Assume it's an image for now
                parts = [instruction, types.Part.from_bytes(data=content, mime_type="image/jpeg")]
            else:
                parts = [instruction, content]

            # Configure generation with schema
            config_params = {
                **self.model_kwargs,
                **kwargs,
                "response_mime_type": "application/json",
                "response_schema": self.schema,
            }

            # Generate structured output
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=parts,
                config=types.GenerateContentConfig(**config_params),
            )

            # Parse response into schema
            if not response.text:
                raise ExtractionError("Empty response from Gemini API")

            return self.schema.model_validate_json(response.text)

        except Exception as e:
            raise ExtractionError(f"Failed to extract structured data: {e}") from e

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
            **kwargs: Additional generation parameters.

        Returns:
            List of structured outputs conforming to the schema.

        Raises:
            ExtractionError: If extraction fails.
        """
        # Simple parallel extraction (can be optimized with batching)
        tasks = [self.extract(content, prompt, **kwargs) for content in contents]
        return await asyncio.gather(*tasks)
