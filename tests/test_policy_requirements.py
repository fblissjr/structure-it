"""Tests for policy requirements extraction."""

import pytest
from pydantic import ValidationError

from structure_it.schemas.policy_requirements import (
    PolicyRequirement,
    PolicyRequirements,
)


class TestPolicyRequirement:
    """Tests for PolicyRequirement schema."""

    def test_create_valid_requirement(self):
        """Test creating a valid policy requirement."""
        req = PolicyRequirement(
            requirement_id="FIN-001-REQ-001",
            statement="All expense reports must be submitted within 30 days.",
            requirement_type="mandatory",
            source_policy_id="FIN-001",
            source_section="Section 3.2",
            applies_to=["All Employees"],
            conditions=["Expense incurred within fiscal year"],
            regulatory_basis=["SOX 404"],
        )

        assert req.requirement_id == "FIN-001-REQ-001"
        assert req.requirement_type == "mandatory"
        assert len(req.applies_to) == 1
        assert "All Employees" in req.applies_to

    def test_requirement_minimal_fields(self):
        """Test requirement with only required fields."""
        req = PolicyRequirement(
            requirement_id="IT-001-REQ-001",
            statement="Users must use strong passwords.",
            requirement_type="mandatory",
            source_policy_id="IT-001",
        )

        assert req.requirement_id == "IT-001-REQ-001"
        assert req.applies_to == []
        assert req.conditions == []
        assert req.exceptions == []
        assert req.regulatory_basis == []

    def test_requirement_types(self):
        """Test different requirement types."""
        for req_type in ["mandatory", "recommended", "prohibited"]:
            req = PolicyRequirement(
                requirement_id=f"TEST-{req_type}",
                statement=f"This is a {req_type} requirement.",
                requirement_type=req_type,
                source_policy_id="TEST-001",
            )
            assert req.requirement_type == req_type

    def test_requirement_to_dict(self):
        """Test converting requirement to dictionary."""
        req = PolicyRequirement(
            requirement_id="FIN-001-REQ-001",
            statement="Test requirement",
            requirement_type="mandatory",
            source_policy_id="FIN-001",
            applies_to=["CFO", "Finance Team"],
        )

        req_dict = req.to_dict()
        assert isinstance(req_dict, dict)
        assert req_dict["requirement_id"] == "FIN-001-REQ-001"
        assert req_dict["applies_to"] == ["CFO", "Finance Team"]

    def test_requirement_to_json(self):
        """Test converting requirement to JSON."""
        req = PolicyRequirement(
            requirement_id="FIN-001-REQ-001",
            statement="Test requirement",
            requirement_type="mandatory",
            source_policy_id="FIN-001",
        )

        req_json = req.to_json()
        assert isinstance(req_json, str)
        assert "FIN-001-REQ-001" in req_json
        assert "mandatory" in req_json


class TestPolicyRequirements:
    """Tests for PolicyRequirements collection schema."""

    def test_create_valid_policy_requirements(self):
        """Test creating a valid policy requirements collection."""
        reqs = PolicyRequirements(
            policy_id="FIN-001",
            policy_title="Expense Reimbursement Policy",
            policy_type="Financial",
            policy_version="1.0",
            effective_date="2024-01-15",
        )

        assert reqs.policy_id == "FIN-001"
        assert reqs.policy_type == "Financial"
        assert reqs.total_requirements == 0

    def test_add_requirements_and_update_counts(self):
        """Test adding requirements and updating counts."""
        reqs = PolicyRequirements(
            policy_id="FIN-001",
            policy_title="Expense Reimbursement Policy",
            policy_type="Financial",
        )

        # Add requirements
        reqs.requirements = [
            PolicyRequirement(
                requirement_id="FIN-001-REQ-001",
                statement="Must submit within 30 days",
                requirement_type="mandatory",
                source_policy_id="FIN-001",
            ),
            PolicyRequirement(
                requirement_id="FIN-001-REQ-002",
                statement="Should include receipts",
                requirement_type="recommended",
                source_policy_id="FIN-001",
            ),
            PolicyRequirement(
                requirement_id="FIN-001-REQ-003",
                statement="Must not exceed budget",
                requirement_type="mandatory",
                source_policy_id="FIN-001",
            ),
            PolicyRequirement(
                requirement_id="FIN-001-REQ-004",
                statement="Prohibited from personal expenses",
                requirement_type="prohibited",
                source_policy_id="FIN-001",
            ),
        ]

        # Update counts
        reqs.update_counts()

        assert reqs.total_requirements == 4
        assert reqs.total_mandatory == 2
        assert reqs.total_recommended == 1
        assert reqs.total_prohibited == 1

    def test_total_requirements_property(self):
        """Test total_requirements property."""
        reqs = PolicyRequirements(
            policy_id="FIN-001",
            policy_title="Test Policy",
            policy_type="Financial",
        )

        assert reqs.total_requirements == 0

        reqs.requirements = [
            PolicyRequirement(
                requirement_id=f"FIN-001-REQ-{i:03d}",
                statement=f"Requirement {i}",
                requirement_type="mandatory",
                source_policy_id="FIN-001",
            )
            for i in range(1, 11)
        ]

        assert reqs.total_requirements == 10

    def test_policy_types(self):
        """Test different policy types."""
        policy_types = ["Financial", "IT Security", "HR", "Legal", "Compliance"]

        for ptype in policy_types:
            reqs = PolicyRequirements(
                policy_id=f"{ptype[:3].upper()}-001",
                policy_title=f"Test {ptype} Policy",
                policy_type=ptype,
            )
            assert reqs.policy_type == ptype

    def test_extraction_metadata(self):
        """Test extraction metadata fields."""
        reqs = PolicyRequirements(
            policy_id="FIN-001",
            policy_title="Test Policy",
            policy_type="Financial",
            extraction_timestamp="2024-01-15T10:30:00",
            model_used="gemini-2.0-flash-exp",
            extraction_notes=["Warning: Some requirements may be ambiguous"],
        )

        assert reqs.extraction_timestamp == "2024-01-15T10:30:00"
        assert reqs.model_used == "gemini-2.0-flash-exp"
        assert len(reqs.extraction_notes) == 1

    def test_to_dict(self):
        """Test converting policy requirements to dictionary."""
        reqs = PolicyRequirements(
            policy_id="FIN-001",
            policy_title="Test Policy",
            policy_type="Financial",
        )

        reqs.requirements = [
            PolicyRequirement(
                requirement_id="FIN-001-REQ-001",
                statement="Test requirement",
                requirement_type="mandatory",
                source_policy_id="FIN-001",
            )
        ]

        reqs_dict = reqs.to_dict()
        assert isinstance(reqs_dict, dict)
        assert reqs_dict["policy_id"] == "FIN-001"
        assert len(reqs_dict["requirements"]) == 1

    def test_to_json(self):
        """Test converting policy requirements to JSON."""
        reqs = PolicyRequirements(
            policy_id="FIN-001",
            policy_title="Test Policy",
            policy_type="Financial",
        )

        reqs_json = reqs.to_json()
        assert isinstance(reqs_json, str)
        assert "FIN-001" in reqs_json
        assert "Test Policy" in reqs_json


class TestRequirementValidation:
    """Tests for requirement validation."""

    def test_empty_statement_allowed(self):
        """Test that empty statements are allowed (will be caught by extractor)."""
        # Pydantic will allow empty strings, validation happens at extraction level
        req = PolicyRequirement(
            requirement_id="TEST-001",
            statement="",
            requirement_type="mandatory",
            source_policy_id="TEST",
        )
        assert req.statement == ""

    def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError):
            PolicyRequirement(
                requirement_id="TEST-001",
                statement="Test",
                requirement_type="mandatory",
                source_policy_id="TEST",
                extra_field="not allowed",  # This should raise an error
            )

    def test_required_fields_enforced(self):
        """Test that required fields are enforced."""
        # Missing requirement_id
        with pytest.raises(ValidationError):
            PolicyRequirement(
                statement="Test",
                requirement_type="mandatory",
                source_policy_id="TEST",
            )

        # Missing statement
        with pytest.raises(ValidationError):
            PolicyRequirement(
                requirement_id="TEST-001",
                requirement_type="mandatory",
                source_policy_id="TEST",
            )

        # Missing requirement_type
        with pytest.raises(ValidationError):
            PolicyRequirement(
                requirement_id="TEST-001",
                statement="Test",
                source_policy_id="TEST",
            )

        # Missing source_policy_id
        with pytest.raises(ValidationError):
            PolicyRequirement(
                requirement_id="TEST-001",
                statement="Test",
                requirement_type="mandatory",
            )


class TestPolicyRequirementsValidation:
    """Tests for policy requirements validation."""

    def test_required_fields_enforced(self):
        """Test that required fields are enforced."""
        # Missing policy_id
        with pytest.raises(ValidationError):
            PolicyRequirements(
                policy_title="Test Policy",
                policy_type="Financial",
            )

        # Missing policy_title
        with pytest.raises(ValidationError):
            PolicyRequirements(
                policy_id="FIN-001",
                policy_type="Financial",
            )

        # Missing policy_type
        with pytest.raises(ValidationError):
            PolicyRequirements(
                policy_id="FIN-001",
                policy_title="Test Policy",
            )

    def test_counts_default_to_zero(self):
        """Test that counts default to zero."""
        reqs = PolicyRequirements(
            policy_id="FIN-001",
            policy_title="Test Policy",
            policy_type="Financial",
        )

        assert reqs.total_mandatory == 0
        assert reqs.total_recommended == 0
        assert reqs.total_prohibited == 0

    def test_requirements_default_to_empty_list(self):
        """Test that requirements default to empty list."""
        reqs = PolicyRequirements(
            policy_id="FIN-001",
            policy_title="Test Policy",
            policy_type="Financial",
        )

        assert reqs.requirements == []
        assert isinstance(reqs.requirements, list)
