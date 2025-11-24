"""Media transcript extractor using Gemini."""

from typing import Any

from structure_it.config import DEFAULT_MODEL
from structure_it.extractors.gemini import GeminiExtractor
from structure_it.schemas.media import MediaTranscript


class MediaExtractor:
    """Extract structured data from media transcripts (e.g., YouTube, podcasts).

    Analyzes transcript content to extract title, description, speakers,
    segments, timestamps, and key takeaways into a standardized MediaTranscript format.
    """

    def __init__(
        self,
        model_name: str | None = None,
        api_key: str | None = None,
        **model_kwargs: Any,
    ) -> None:
        """Initialize the media transcript extractor.

        Args:
            model_name: Gemini model to use (defaults to config.DEFAULT_MODEL).
            api_key: Google API key (if not set via environment).
            **model_kwargs: Additional model configuration parameters.
        """
        self.model_name = model_name or DEFAULT_MODEL
        self.extractor = GeminiExtractor(
            schema=MediaTranscript,
            model_name=self.model_name,
            api_key=api_key,
            **model_kwargs,
        )

    def _build_extraction_prompt(self) -> str:
        """Build extraction prompt for media transcripts."""
        return """Analyze the following media transcript (e.g., from a YouTube video or podcast) and extract structured information.

Focus on extracting:
1. Media title and a concise description.
2. Channel/show name, host, and any guests (with their roles if available).
3. Metadata like duration, publish date, episode/season numbers, category, and tags.
4. An overall summary and a list of key takeaways.
5. Segments or chapters with titles, start/end times, summaries, and key points discussed.
6. Important timestamps mentioned in the transcript or implied by significant topic shifts.
7. Any resources mentioned (books, websites, tools) with titles and URLs.
8. Topics discussed, questions answered, and notable quotes.

Be thorough and extract all relevant details into the structured format.
If a field is not explicitly mentioned, leave it as None or an empty list.
"""

    async def extract(
        self,
        content: str,
        **kwargs: Any,
    ) -> MediaTranscript:
        """Extract structured data from media transcript.

        Args:
            content: Media transcript text.
            **kwargs: Additional generation parameters.

        Returns:
            MediaTranscript object.
        """
        prompt = self._build_extraction_prompt()

        # Extract
        transcript_data = await self.extractor.extract(
            content=content,
            prompt=prompt,
            **kwargs,
        )
        return transcript_data
