"""Meeting notes extractor using Gemini."""

from typing import Any

from structure_it.config import DEFAULT_MODEL
from structure_it.extractors.gemini import GeminiExtractor
from structure_it.schemas.meetings import MeetingNote


class MeetingExtractor:
    """Extract structured meeting notes from transcript or text.

    Analyzes meeting content to extract participants, topics, decisions,
    and action items into a standardized MeetingNote format.
    """

    def __init__(
        self,
        model_name: str | None = None,
        api_key: str | None = None,
        **model_kwargs: Any,
    ) -> None:
        """Initialize the meeting notes extractor.

        Args:
            model_name: Gemini model to use (defaults to config.DEFAULT_MODEL).
            api_key: Google API key (if not set via environment).
            **model_kwargs: Additional model configuration parameters.
        """
        self.model_name = model_name or DEFAULT_MODEL
        self.extractor = GeminiExtractor(
            schema=MeetingNote,
            model_name=self.model_name,
            api_key=api_key,
            **model_kwargs,
        )

    def _build_extraction_prompt(self) -> str:
        """Build extraction prompt for meeting notes."""
        return """Analyze the following meeting transcript/notes and extract structured information.

Focus on extracting:
1. Meeting title, date, start/end times, duration.
2. Participants: names, and their roles if mentioned.
3. Agenda items or main topics discussed, with summaries and key discussion points.
4. Decisions made: descriptions, rationale, who made them, and alternatives considered.
5. Action items: clear descriptions, assignees, due dates, and priority.
6. Overall meeting summary and key takeaways.
7. Any next steps or follow-up required.

Be thorough and extract all relevant details into the structured format.
If a field is not explicitly mentioned, leave it as None or an empty list.
"""

    async def extract(
        self,
        content: str,
        **kwargs: Any,
    ) -> MeetingNote:
        """Extract structured meeting notes.

        Args:
            content: Meeting transcript or notes text.
            **kwargs: Additional generation parameters.

        Returns:
            MeetingNote object.
        """
        prompt = self._build_extraction_prompt()

        # Extract
        notes = await self.extractor.extract(
            content=content,
            prompt=prompt,
            **kwargs,
        )
        return notes
