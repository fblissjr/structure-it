"""Schema for policy requirements extraction."""

from pydantic import ConfigDict

from structure_it.schemas.base import BaseSchema


class PolicyRequirement(BaseSchema):
    """A single requirement extracted from a policy document.

    Represents an individual obligation, recommendation, or prohibition
    found within a policy document, with metadata about its applicability.
    """

    # Override BaseSchema config for Gemini API compatibility
    # (Gemini doesn't support additionalProperties in JSON schema)
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        strict=False,
        extra="ignore",  # Changed from "forbid" to avoid additionalProperties
    )

    requirement_id: str
    statement: str
    requirement_type: str  # "mandatory", "recommended", "prohibited"

    # Source information
    source_policy_id: str
    source_section: str | None = None

    # Applicability
    applies_to: list[str] = []  # Roles, departments, systems
    conditions: list[str] = []  # When this requirement applies
    exceptions: list[str] = []  # When this requirement does NOT apply

    # Regulatory context
    regulatory_basis: list[str] = []  # e.g., "SOX 404", "GDPR Article 32"

    # Optional metadata
    priority: str | None = None  # "high", "medium", "low"
    enforcement_mechanism: str | None = None  # How compliance is verified


class PolicyRequirements(BaseSchema):
    """Collection of requirements extracted from a policy document.

    Wrapper class containing all requirements from a single policy,
    with summary metadata and counts.
    """

    # Override BaseSchema config for Gemini API compatibility
    # (Gemini doesn't support additionalProperties in JSON schema)
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        strict=False,
        extra="ignore",  # Changed from "forbid" to avoid additionalProperties
    )

    policy_id: str
    policy_title: str
    policy_type: str  # "Financial", "IT Security", "HR", "Legal", "Compliance"
    policy_version: str | None = None
    effective_date: str | None = None

    # Extracted requirements
    requirements: list[PolicyRequirement] = []

    # Summary counts
    total_mandatory: int = 0
    total_recommended: int = 0
    total_prohibited: int = 0

    # Metadata
    extraction_timestamp: str | None = None
    model_used: str | None = None
    extraction_notes: list[str] = []  # Warnings, issues during extraction

    def update_counts(self) -> None:
        """Update summary counts based on requirements list."""
        self.total_mandatory = sum(
            1 for r in self.requirements if r.requirement_type == "mandatory"
        )
        self.total_recommended = sum(
            1 for r in self.requirements if r.requirement_type == "recommended"
        )
        self.total_prohibited = sum(
            1 for r in self.requirements if r.requirement_type == "prohibited"
        )

    @property
    def total_requirements(self) -> int:
        """Total number of requirements extracted."""
        return len(self.requirements)
