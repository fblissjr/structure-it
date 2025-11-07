"""Base schema definitions for structured outputs."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base class for all structured output schemas.

    Provides common configuration for Pydantic models used in structured extraction.
    All schema classes should inherit from this base class.
    """

    model_config = ConfigDict(
        # Allow validation of arbitrary types
        arbitrary_types_allowed=True,
        # Validate on assignment
        validate_assignment=True,
        # Strict mode for better type safety
        strict=False,
        # Extra fields are forbidden
        extra="forbid",
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert schema to dictionary representation.

        Returns:
            Dictionary representation of the schema.
        """
        return self.model_dump(mode="json")

    def to_json(self) -> str:
        """Convert schema to JSON string.

        Returns:
            JSON string representation of the schema.
        """
        return self.model_dump_json(indent=2)
