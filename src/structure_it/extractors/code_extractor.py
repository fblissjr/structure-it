"""Code documentation extractor using Gemini."""

from pathlib import Path
from typing import Any

from structure_it.config import DEFAULT_MODEL
from structure_it.extractors.gemini import GeminiExtractor
from structure_it.schemas.code_docs import CodeDocumentation


class CodeDocsExtractor:
    """Extract structured documentation from source code files.

    Analyzes code to extract modules, classes, functions, parameters,
    and return values into a standardized documentation format.
    """

    def __init__(
        self,
        model_name: str | None = None,
        api_key: str | None = None,
        **model_kwargs: Any,
    ) -> None:
        """Initialize the code docs extractor.

        Args:
            model_name: Gemini model to use (defaults to config.DEFAULT_MODEL).
            api_key: Google API key (if not set via environment).
            **model_kwargs: Additional model configuration parameters.
        """
        super().__init__() # Call the superclass constructor if BaseExtractor was inherited
        self.model_name = model_name or DEFAULT_MODEL
        self.extractor = GeminiExtractor(
            schema=CodeDocumentation,
            model_name=self.model_name,
            api_key=api_key,
            **model_kwargs,
        )

    def _build_extraction_prompt(self, language: str) -> str:
        """Build extraction prompt for code documentation.

        Args:
            language: Programming language of the source file.

        Returns:
            Extraction prompt text.
        """
        return f"""Analyze this {language} source code and extract comprehensive documentation.

Focus on extracting:
1. Module-level documentation (purpose, description, exports)
2. Classes with their attributes, methods, and inheritance
3. Functions with precise signatures, parameters (including types and defaults), and return values
4. Usage examples inferred from the code or docstrings
5. Dependencies and external imports

For every function/method:
- Extract the full signature
- specific input parameters and their types
- description of what it does
- what it returns

For every class:
- Extract attributes and their types
- List all methods

If docstrings exist, use them as the primary source of truth but enhance them with
inferred details from the code implementation.
"""

    async def extract(
        self,
        file_path: str | Path,
        **kwargs: Any,
    ) -> CodeDocumentation:
        """Extract documentation from a code file.

        Args:
            file_path: Path to the source code file.
            **kwargs: Additional generation parameters.

        Returns:
            CodeDocumentation object.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise ValueError(f"File not found: {file_path}")

        # Detect language from extension
        suffix = file_path.suffix.lower()
        language_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".go": "Go",
            ".rs": "Rust",
            ".cpp": "C++",
            ".c": "C",
        }
        language = language_map.get(suffix, "Unknown")

        content = file_path.read_text(encoding="utf-8")
        prompt = self._build_extraction_prompt(language)

        # Extract
        docs = await self.extractor.extract(
            content=content,
            prompt=prompt,
            **kwargs,
        )

        # Post-process metadata
        docs.file_path = str(file_path)
        docs.language = language
        
        return docs
