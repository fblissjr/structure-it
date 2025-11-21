"""Tests for policy requirements extractor."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from structure_it.extractors.policy_extractor import PolicyRequirementsExtractor
from structure_it.schemas.policy_requirements import PolicyRequirement, PolicyRequirements


# Mock API key for all tests
@pytest.fixture(autouse=True)
def mock_api_key(monkeypatch):
    """Automatically mock API key for all tests."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")


class TestPolicyRequirementsExtractor:
    """Tests for PolicyRequirementsExtractor."""

    def test_init_default_model(self):
        """Test initialization with default model."""
        extractor = PolicyRequirementsExtractor()
        assert extractor.model_name == "gemini-2.5-flash"

    def test_init_custom_model(self):
        """Test initialization with custom model."""
        extractor = PolicyRequirementsExtractor(model_name="gemini-2.5-pro")
        assert extractor.model_name == "gemini-2.5-pro"

    def test_generate_requirement_id(self):
        """Test requirement ID generation."""
        extractor = PolicyRequirementsExtractor()

        req_id = extractor._generate_requirement_id("FIN-001", 1)
        assert req_id == "FIN-001-REQ-001"

        req_id = extractor._generate_requirement_id("IT-042", 123)
        assert req_id == "IT-042-REQ-123"

    def test_build_extraction_prompt_financial(self):
        """Test building extraction prompt for Financial policy."""
        extractor = PolicyRequirementsExtractor()
        prompt = extractor._build_extraction_prompt("Financial")

        assert "Financial" in prompt
        assert "approval thresholds" in prompt.lower()
        assert "authorization levels" in prompt.lower()
        assert "must" in prompt
        assert "shall" in prompt
        assert "mandatory" in prompt

    def test_build_extraction_prompt_it_security(self):
        """Test building extraction prompt for IT Security policy."""
        extractor = PolicyRequirementsExtractor()
        prompt = extractor._build_extraction_prompt("IT Security")

        assert "IT Security" in prompt
        assert "access control" in prompt.lower()
        assert "technical control" in prompt.lower()

    def test_build_extraction_prompt_hr(self):
        """Test building extraction prompt for HR policy."""
        extractor = PolicyRequirementsExtractor()
        prompt = extractor._build_extraction_prompt("HR")

        assert "HR" in prompt
        assert "employee" in prompt.lower()
        assert "performance" in prompt.lower()

    def test_build_extraction_prompt_legal(self):
        """Test building extraction prompt for Legal policy."""
        extractor = PolicyRequirementsExtractor()
        prompt = extractor._build_extraction_prompt("Legal")

        assert "Legal" in prompt
        assert "regulatory" in prompt.lower()

    def test_build_extraction_prompt_compliance(self):
        """Test building extraction prompt for Compliance policy."""
        extractor = PolicyRequirementsExtractor()
        prompt = extractor._build_extraction_prompt("Compliance")

        assert "Compliance" in prompt
        assert "regulatory framework" in prompt.lower()

    @pytest.mark.asyncio
    async def test_extract_missing_metadata_fields(self):
        """Test that extraction fails with missing metadata."""
        extractor = PolicyRequirementsExtractor()

        # Missing policy_id
        with pytest.raises(ValueError, match="Missing required metadata"):
            await extractor.extract(
                pdf_path="test.pdf",
                policy_metadata={
                    "policy_title": "Test Policy",
                    "policy_type": "Financial",
                },
            )

        # Missing policy_title
        with pytest.raises(ValueError, match="Missing required metadata"):
            await extractor.extract(
                pdf_path="test.pdf",
                policy_metadata={
                    "policy_id": "FIN-001",
                    "policy_type": "Financial",
                },
            )

        # Missing policy_type
        with pytest.raises(ValueError, match="Missing required metadata"):
            await extractor.extract(
                pdf_path="test.pdf",
                policy_metadata={
                    "policy_id": "FIN-001",
                    "policy_title": "Test Policy",
                },
            )

    def test_convert_pdf_to_markdown_file_not_found(self):
        """Test PDF conversion with non-existent file."""
        extractor = PolicyRequirementsExtractor()

        with pytest.raises(ValueError, match="File not found"):
            extractor._convert_to_markdown("nonexistent.pdf")

    @pytest.mark.asyncio
    @patch("structure_it.extractors.policy_extractor.MarkItDown")
    @patch("structure_it.extractors.gemini.GeminiExtractor.extract")
    async def test_extract_success(self, mock_extract, mock_markitdown):
        """Test successful extraction."""
        # Mock PDF conversion
        mock_md_instance = MagicMock()
        mock_md_instance.convert.return_value.text_content = "# Test Policy\n\nEmployees must submit reports."
        mock_markitdown.return_value = mock_md_instance

        # Mock extraction result
        mock_requirements = PolicyRequirements(
            policy_id="FIN-001",
            policy_title="Test Policy",
            policy_type="Financial",
            requirements=[
                PolicyRequirement(
                    requirement_id="",  # Will be auto-generated
                    statement="Employees must submit reports",
                    requirement_type="mandatory",
                    source_policy_id="",  # Will be set by extractor
                )
            ],
        )
        mock_extract.return_value = mock_requirements

        # Create a temporary test file
        test_pdf = Path("test_policy.pdf")
        test_pdf.write_text("dummy pdf content")

        try:
            extractor = PolicyRequirementsExtractor()
            result = await extractor.extract(
                pdf_path=test_pdf,
                policy_metadata={
                    "policy_id": "FIN-001",
                    "policy_title": "Test Policy",
                    "policy_type": "Financial",
                },
            )

            # Verify results
            assert result.policy_id == "FIN-001"
            assert result.policy_title == "Test Policy"
            assert result.policy_type == "Financial"
            assert len(result.requirements) == 1

            # Verify requirement ID was generated
            assert result.requirements[0].requirement_id == "FIN-001-REQ-001"
            # Verify source_policy_id was set
            assert result.requirements[0].source_policy_id == "FIN-001"

            # Verify counts were updated
            assert result.total_mandatory >= 0  # update_counts was called

        finally:
            # Cleanup
            if test_pdf.exists():
                test_pdf.unlink()

    @pytest.mark.asyncio
    @patch("structure_it.extractors.policy_extractor.MarkItDown")
    @patch("structure_it.extractors.gemini.GeminiExtractor.extract")
    async def test_extract_with_optional_metadata(self, mock_extract, mock_markitdown):
        """Test extraction with optional metadata fields."""
        # Mock PDF conversion
        mock_md_instance = MagicMock()
        mock_md_instance.convert.return_value.text_content = "# Test Policy"
        mock_markitdown.return_value = mock_md_instance

        # Mock extraction result
        mock_requirements = PolicyRequirements(
            policy_id="FIN-001",
            policy_title="Test Policy",
            policy_type="Financial",
            requirements=[],
        )
        mock_extract.return_value = mock_requirements

        # Create a temporary test file
        test_pdf = Path("test_policy.pdf")
        test_pdf.write_text("dummy pdf content")

        try:
            extractor = PolicyRequirementsExtractor()
            result = await extractor.extract(
                pdf_path=test_pdf,
                policy_metadata={
                    "policy_id": "FIN-001",
                    "policy_title": "Test Policy",
                    "policy_type": "Financial",
                    "policy_version": "1.0",
                    "effective_date": "2024-01-15",
                },
            )

            # Metadata should be preserved
            assert result.policy_id == "FIN-001"
            # Extraction timestamp should be set
            assert result.extraction_timestamp is not None
            # Model should be set
            assert result.model_used == "gemini-2.5-flash"

        finally:
            # Cleanup
            if test_pdf.exists():
                test_pdf.unlink()

    def test_requirement_id_generation_format(self):
        """Test requirement ID format consistency."""
        extractor = PolicyRequirementsExtractor()

        # Test various indices
        test_cases = [
            ("FIN-001", 1, "FIN-001-REQ-001"),
            ("IT-042", 5, "IT-042-REQ-005"),
            ("HR-100", 99, "HR-100-REQ-099"),
            ("LEG-001", 100, "LEG-001-REQ-100"),
        ]

        for policy_id, index, expected in test_cases:
            result = extractor._generate_requirement_id(policy_id, index)
            assert result == expected


class TestPolicyExtractorPrompts:
    """Tests for extraction prompt generation."""

    def test_all_policy_types_have_prompts(self):
        """Test that all policy types generate valid prompts."""
        extractor = PolicyRequirementsExtractor()
        policy_types = ["Financial", "IT Security", "HR", "Legal", "Compliance"]

        for policy_type in policy_types:
            prompt = extractor._build_extraction_prompt(policy_type)

            # All prompts should have base content
            assert "requirement" in prompt.lower()
            assert "must" in prompt
            assert policy_type in prompt

            # Should be reasonably long
            assert len(prompt) > 200

    def test_unknown_policy_type_gets_base_prompt(self):
        """Test that unknown policy types get base prompt without domain guidance."""
        extractor = PolicyRequirementsExtractor()
        prompt = extractor._build_extraction_prompt("Unknown Type")

        # Should still have base prompt
        assert "requirement" in prompt.lower()
        assert "must" in prompt
        # Should not crash
        assert len(prompt) > 0
