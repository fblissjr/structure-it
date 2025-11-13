"""Policy requirements extractor using Gemini."""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any

from markitdown import MarkItDown

from structure_it.extractors.gemini import GeminiExtractor
from structure_it.schemas.policy_requirements import PolicyRequirements


class PolicyRequirementsExtractor:
    """Extract structured requirements from policy documents.

    Uses markitdown to convert PDFs to markdown, then extracts
    requirements using Gemini with a focused prompt.
    """

    def __init__(
        self,
        model_name: str = "gemini-2.5-flash-lite",
        api_key: str | None = None,
        **model_kwargs: Any,
    ) -> None:
        """Initialize the policy requirements extractor.

        Args:
            model_name: Gemini model to use (default: gemini-2.5-flash).
            api_key: Google API key (if not set via environment).
            **model_kwargs: Additional model configuration parameters.
        """
        self.model_name = model_name
        self.extractor = GeminiExtractor(
            schema=PolicyRequirements,
            model_name=model_name,
            api_key=api_key,
            **model_kwargs,
        )
        self.markdown_converter = MarkItDown()

    def _convert_pdf_to_markdown(self, pdf_path: str | Path) -> str:
        """Convert PDF to markdown text.

        Args:
            pdf_path: Path to PDF file.

        Returns:
            Markdown content of the PDF.

        Raises:
            ValueError: If file doesn't exist or conversion fails.
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise ValueError(f"PDF file not found: {pdf_path}")

        result = self.markdown_converter.convert(str(pdf_path))
        return result.text_content

    def _build_extraction_prompt(self, policy_type: str) -> str:
        """Build extraction prompt for a policy type.

        Args:
            policy_type: Type of policy (Financial, IT Security, HR, Legal, Compliance).

        Returns:
            Extraction prompt text.
        """
        base_prompt = f"""Extract ALL requirements from this {policy_type} policy document.

A requirement is any statement that:
- Uses obligation language: "must", "shall", "will", "required to", "should", "recommended", "prohibited"
- Specifies an action, restriction, or recommendation
- Has a clear subject (who/what it applies to)

For each requirement:
1. Extract the exact statement (or paraphrase if needed for clarity)
2. Classify as:
   - "mandatory" for must/shall/will/required to
   - "recommended" for should/recommended/encouraged
   - "prohibited" for must not/shall not/prohibited/forbidden
3. Identify who/what it applies to (roles, departments, systems, employees)
4. Note any conditions ("when X happens", "if Y exceeds threshold")
5. Note any exceptions ("except for Z", "unless A")
6. If mentioned, capture regulatory basis (SOX, GDPR, PCI-DSS, HIPAA, etc.)

Be thorough - include all requirements, even minor ones.
"""

        # Add domain-specific guidance
        domain_guidance = {
            "Financial": """
Pay special attention to:
- Approval thresholds and authorization levels
- Spending limits and budget controls
- Financial reporting requirements
- Audit and documentation requirements
""",
            "IT Security": """
Pay special attention to:
- Access controls and authentication requirements
- Technical controls (encryption, logging, monitoring)
- Incident response procedures
- System configuration requirements
""",
            "HR": """
Pay special attention to:
- Employee obligations and conduct
- Performance criteria and expectations
- Leave and absence requirements
- Grievance and disciplinary procedures
""",
            "Legal": """
Pay special attention to:
- Regulatory obligations and citations
- Disclosure requirements
- Compliance deadlines
- Risk statements and prohibitions
""",
            "Compliance": """
Pay special attention to:
- Regulatory framework references
- Monitoring and reporting requirements
- Audit and verification procedures
- Certification requirements
""",
        }

        guidance = domain_guidance.get(policy_type, "")
        return base_prompt + guidance

    def _generate_requirement_id(self, policy_id: str, index: int) -> str:
        """Generate unique requirement ID.

        Args:
            policy_id: Policy identifier.
            index: Requirement index within policy.

        Returns:
            Unique requirement ID.
        """
        # Format: POLICY-REQ-###
        return f"{policy_id}-REQ-{index:03d}"

    async def extract(
        self,
        pdf_path: str | Path,
        policy_metadata: dict[str, Any],
        **kwargs: Any,
    ) -> PolicyRequirements:
        """Extract requirements from a policy PDF.

        Args:
            pdf_path: Path to the policy PDF file.
            policy_metadata: Metadata about the policy containing:
                - policy_id: Unique policy identifier
                - policy_title: Policy name
                - policy_type: Type (Financial, IT Security, HR, Legal, Compliance)
                - policy_version: Optional version string
                - effective_date: Optional effective date string
            **kwargs: Additional generation parameters.

        Returns:
            PolicyRequirements object with all extracted requirements.

        Raises:
            ValueError: If required metadata is missing.
            ExtractionError: If extraction fails.
        """
        # Validate required metadata
        required_fields = ["policy_id", "policy_title", "policy_type"]
        missing = [f for f in required_fields if f not in policy_metadata]
        if missing:
            raise ValueError(f"Missing required metadata fields: {missing}")

        policy_id = policy_metadata["policy_id"]
        policy_title = policy_metadata["policy_title"]
        policy_type = policy_metadata["policy_type"]

        # Convert PDF to markdown
        markdown_content = self._convert_pdf_to_markdown(pdf_path)

        # Build extraction prompt
        prompt = self._build_extraction_prompt(policy_type)

        # Extract requirements
        extraction_timestamp = datetime.utcnow().isoformat()
        requirements = await self.extractor.extract(
            content=markdown_content,
            prompt=prompt,
            **kwargs,
        )

        # Post-process: Generate requirement IDs
        for idx, req in enumerate(requirements.requirements, start=1):
            if not req.requirement_id or req.requirement_id == "":
                req.requirement_id = self._generate_requirement_id(policy_id, idx)
            # Ensure policy_id is set
            req.source_policy_id = policy_id

        # Update counts
        requirements.update_counts()

        # Add extraction metadata
        requirements.extraction_timestamp = extraction_timestamp
        requirements.model_used = self.model_name

        return requirements

    async def extract_batch(
        self,
        pdf_paths: list[tuple[str | Path, dict[str, Any]]],
        **kwargs: Any,
    ) -> list[PolicyRequirements]:
        """Extract requirements from multiple policy PDFs.

        Args:
            pdf_paths: List of (pdf_path, policy_metadata) tuples.
            **kwargs: Additional generation parameters.

        Returns:
            List of PolicyRequirements objects.
        """
        import asyncio

        tasks = [self.extract(pdf_path, metadata, **kwargs) for pdf_path, metadata in pdf_paths]
        return await asyncio.gather(*tasks, return_exceptions=True)
