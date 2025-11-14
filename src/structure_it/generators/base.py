"""Base generator for creating synthetic content with LLMs."""

import asyncio
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types

from structure_it.config import DEFAULT_MODEL, DEFAULT_TEMPERATURE


class BaseGenerator:
    """Base class for LLM-powered content generators.

    Provides common functionality for generating synthetic content,
    managing API clients, and saving outputs.
    """

    def __init__(
        self,
        model_name: str | None = None,
        temperature: float | None = None,
        api_key: str | None = None,
    ) -> None:
        """Initialize the generator.

        Args:
            model_name: Gemini model to use (defaults to config.DEFAULT_MODEL).
            temperature: Sampling temperature (defaults to config.DEFAULT_TEMPERATURE).
            api_key: Google API key (if not set via environment).
        """
        self.model_name = model_name or DEFAULT_MODEL
        self.temperature = temperature or DEFAULT_TEMPERATURE

        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = genai.Client()

    async def generate_text(
        self,
        prompt: str,
        temperature: float | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate text using the LLM.

        Args:
            prompt: Generation prompt.
            temperature: Optional temperature override.
            **kwargs: Additional generation config parameters.

        Returns:
            Generated text content.
        """
        temp = temperature if temperature is not None else self.temperature

        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temp,
                **kwargs,
            ),
        )

        return response.text

    def save_as_markdown(self, content: str, output_path: Path) -> None:
        """Save content as markdown file.

        Args:
            content: Text content to save.
            output_path: Output file path.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

    def get_model_info(self) -> dict[str, Any]:
        """Get current model configuration.

        Returns:
            Dictionary with model name and temperature.
        """
        return {
            "model": self.model_name,
            "temperature": self.temperature,
        }
